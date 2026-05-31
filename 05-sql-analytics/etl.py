#!/usr/bin/env python3
"""
ETL-пайплайн: CSV → SQLite (3NF) + аналитическая витрина.
Проект 5: SQL Analytics
"""

import sqlite3
import csv
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
CSV_PATH = BASE_DIR.parent / '04-retail-rfm-analysis' / 'online_retail.csv'
DB_PATH = BASE_DIR / 'retail_analytics.db'

def init_database():
    """Создаём нормализованную схему (3NF)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Очищаем если есть
    cursor.executescript("""
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;
        DROP TABLE IF EXISTS countries;
        
        -- Справочник стран
        CREATE TABLE countries (
            country_id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_name TEXT UNIQUE NOT NULL
        );
        
        -- Клиенты (2NF)
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            country_id INTEGER,
            first_purchase_date TEXT,
            last_purchase_date TEXT,
            total_orders INTEGER DEFAULT 0,
            total_spent REAL DEFAULT 0,
            FOREIGN KEY (country_id) REFERENCES countries(country_id)
        );
        
        -- Продукты (2NF)
        CREATE TABLE products (
            stock_code TEXT PRIMARY KEY,
            description TEXT
        );
        
        -- Заказы (3NF)
        CREATE TABLE orders (
            invoice_no TEXT PRIMARY KEY,
            customer_id INTEGER,
            invoice_date TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        
        -- Строки заказа (3NF)
        CREATE TABLE order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_no TEXT,
            stock_code TEXT,
            quantity INTEGER,
            unit_price REAL,
            line_total REAL GENERATED ALWAYS AS (quantity * unit_price) STORED,
            FOREIGN KEY (invoice_no) REFERENCES orders(invoice_no),
            FOREIGN KEY (stock_code) REFERENCES products(stock_code)
        );
        
        -- Индексы для скорости
        CREATE INDEX idx_orders_customer ON orders(customer_id);
        CREATE INDEX idx_orders_date ON orders(invoice_date);
        CREATE INDEX idx_items_invoice ON order_items(invoice_no);
        CREATE INDEX idx_items_stock ON order_items(stock_code);
        CREATE INDEX idx_customers_country ON customers(country_id);
    """)
    
    conn.commit()
    conn.close()
    print("✅ Схема создана (3NF): countries, customers, products, orders, order_items")


def load_data():
    """Загружаем CSV в нормализованные таблицы."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    countries = set()
    customers = {}
    products = {}
    orders = set()
    
    row_count = 0
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Страна
            country = row.get('Country', 'Unknown')
            countries.add(country)
            
            # Клиент
            cust_id = int(float(row['CustomerID'])) if row.get('CustomerID') else None
            if cust_id and cust_id not in customers:
                customers[cust_id] = {
                    'country': country,
                    'first_date': row['InvoiceDate'],
                    'last_date': row['InvoiceDate'],
                    'orders': 0,
                    'spent': 0.0,
                }
            elif cust_id:
                customers[cust_id]['last_date'] = row['InvoiceDate']
            
            # Продукт
            stock = row.get('StockCode', '')
            if stock and stock not in products:
                products[stock] = row.get('Description', '')
            
            # Заказ
            invoice = row.get('InvoiceNo', '')
            if invoice and invoice not in orders:
                orders.add(invoice)
                if cust_id:
                    customers[cust_id]['orders'] += 1
            
            row_count += 1
    
    # Вставляем страны
    country_map = {}
    for country in sorted(countries):
        cursor.execute("INSERT OR IGNORE INTO countries (country_name) VALUES (?)", (country,))
    conn.commit()
    
    cursor.execute("SELECT country_id, country_name FROM countries")
    for cid, cname in cursor.fetchall():
        country_map[cname] = cid
    
    # Вставляем клиентов
    for cust_id, data in customers.items():
        cid = country_map.get(data['country'], 1)
        cursor.execute("""
            INSERT INTO customers (customer_id, country_id, first_purchase_date, last_purchase_date, total_orders, total_spent)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (cust_id, cid, data['first_date'], data['last_date'], data['orders'], data['spent']))
    
    # Вставляем продукты
    for stock, desc in products.items():
        cursor.execute("INSERT OR IGNORE INTO products (stock_code, description) VALUES (?, ?)", (stock, desc))
    
    conn.commit()
    
    # Вставляем заказы и строки
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        order_batch = []
        item_batch = []
        
        for row in reader:
            invoice = row.get('InvoiceNo', '')
            cust_id = int(float(row['CustomerID'])) if row.get('CustomerID') else None
            date_str = row['InvoiceDate']
            
            if invoice and cust_id:
                order_batch.append((invoice, cust_id, date_str))
            
            stock = row.get('StockCode', '')
            qty = int(row.get('Quantity', 0))
            price = float(row.get('UnitPrice', 0))
            
            if invoice and stock and qty > 0 and price > 0:
                item_batch.append((invoice, stock, qty, price))
        
        # Deduplicate orders
        seen_orders = set()
        unique_orders = []
        for o in order_batch:
            if o[0] not in seen_orders:
                seen_orders.add(o[0])
                unique_orders.append(o)
        
        cursor.executemany("INSERT OR IGNORE INTO orders (invoice_no, customer_id, invoice_date) VALUES (?, ?, ?)", unique_orders)
        cursor.executemany("INSERT INTO order_items (invoice_no, stock_code, quantity, unit_price) VALUES (?, ?, ?, ?)", item_batch)
    
    conn.commit()
    conn.close()
    print(f"✅ Загружено: {row_count:,} строк → {len(countries)} стран, {len(customers)} клиентов, {len(products)} продуктов, {len(orders)} заказов")
    return row_count


def update_customer_metrics():
    """Обновляем агрегаты в customers."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE customers
        SET total_spent = (
            SELECT COALESCE(SUM(oi.line_total), 0)
            FROM orders o
            JOIN order_items oi ON o.invoice_no = oi.invoice_no
            WHERE o.customer_id = customers.customer_id
        ),
        total_orders = (
            SELECT COUNT(DISTINCT o.invoice_no)
            FROM orders o
            WHERE o.customer_id = customers.customer_id
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Агрегаты customers обновлены")


if __name__ == "__main__":
    print("🚀 ETL: CSV → SQLite (3NF)")
    print(f"📂 База данных: {DB_PATH}")
    print(f"📊 Источник: {CSV_PATH}")
    print()
    
    init_database()
    rows = load_data()
    update_customer_metrics()
    
    print()
    print("="*60)
    print("🎉 ETL ЗАВЕРШЁН")
    print("="*60)
    print(f"📁 База: {DB_PATH}")
    print(f"📊 Записей загружено: {rows:,}")
    print()
    print("Таблицы:")
    print("  • countries     — справочник стран")
    print("  • customers     — клиенты + агрегаты")
    print("  • products      — справочник товаров")
    print("  • orders        — заказы (header)")
    print("  • order_items   — строки заказа")
    print()
