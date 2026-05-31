#!/usr/bin/env python3
"""
Проект 6: ETL-пайплайн CSV → SQLite → Аналитическая витрина → Отчёт.
Автоматизация: закинул CSV → получил готовую БД + SQL-витрину + PDF.
"""

import argparse
import csv
import sqlite3
import subprocess
import sys
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Цвета
NAVY = HexColor('#1E2761')
ICE = HexColor('#CADCFC')
ACCENT = HexColor('#4a90e2')
DARK = HexColor('#1a1a2e')
LIGHT = HexColor('#f5f7fa')
GREEN = HexColor('#28a745')
RED = HexColor('#dc3545')
ORANGE = HexColor('#fd7e14')

try:
    pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
    FONT = 'DejaVu'
    FONT_B = 'DejaVu-Bold'
except:
    FONT = 'Helvetica'
    FONT_B = 'Helvetica-Bold'

W, H = landscape(A4)

def draw_rounded_rect(c, x, y, w, h, r, fill):
    c.setFillColor(fill)
    c.setStrokeColor(fill)
    p = c.beginPath()
    p.moveTo(x + r, y)
    p.lineTo(x + w - r, y)
    p.arcTo(x + w - r, y, x + w, y + r, r, r)
    p.lineTo(x + w, y + h - r)
    p.arcTo(x + w, y + h - r, x + w - r, y + h, r, r)
    p.lineTo(x + r, y + h)
    p.arcTo(x + r, y + h, x, y + h - r, r, r)
    p.lineTo(x, y + r)
    p.arcTo(x, y + r, x + r, y, r, r)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

def wrap_lines(c, text, max_w, font, size):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = cur + " " + w if cur else w
        if c.stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

class ETLPipeline:
    """Полный пайплайн: CSV → SQLite → Витрина → PDF."""
    
    def __init__(self, csv_path, output_dir):
        self.csv_path = Path(csv_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.output_dir / 'pipeline.db'
        self.row_count = 0
        
    def run(self):
        print("🚀 ETL Pipeline запущен")
        print(f"📁 CSV: {self.csv_path}")
        print(f"📂 Выход: {self.output_dir}")
        
        # Шаг 1: Загрузка CSV
        self.step1_load_csv()
        
        # Шаг 2: Нормализация
        self.step2_normalize()
        
        # Шаг 3: Аналитическая витрина
        self.step3_create_mart()
        
        # Шаг 4: SQL-аналитика
        insights = self.step4_analyze()
        
        # Шаг 5: Визуализация
        png_path = self.step5_visualize()
        
        # Шаг 6: PDF-отчёт
        pdf_path = self.step6_generate_pdf(insights, png_path)
        
        print("\n" + "="*60)
        print("🎉 ETL PIPELINE ЗАВЕРШЁН")
        print("="*60)
        print(f"📁 База данных: {self.db_path}")
        print(f"📊 Записей: {self.row_count:,}")
        print(f"🎨 Дашборд: {png_path}")
        print(f"📄 PDF отчёт: {pdf_path}")
        print("="*60)
        
    def step1_load_csv(self):
        """Шаг 1: Загружаем CSV в staging-таблицу."""
        print("\n📥 Шаг 1: Загрузка CSV в staging...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Читаем заголовки
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            
        # Создаём staging
        cols = ', '.join([f'"{h}" TEXT' for h in headers])
        cursor.execute(f'DROP TABLE IF EXISTS staging')
        cursor.execute(f'CREATE TABLE staging ({cols})')
        
        # Загружаем данные
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = []
            batch_size = 5000
            for row in reader:
                rows.append(tuple(row.get(h, '') for h in headers))
                self.row_count += 1
                if len(rows) >= batch_size:
                    placeholders = ', '.join(['?' for _ in headers])
                    cursor.executemany(f'INSERT INTO staging VALUES ({placeholders})', rows)
                    rows = []
                    if self.row_count % 20000 == 0:
                        print(f"   ... загружено {self.row_count:,} строк")
            if rows:
                placeholders = ', '.join(['?' for _ in headers])
                cursor.executemany(f'INSERT INTO staging VALUES ({placeholders})', rows)
        
        conn.commit()
        conn.close()
        print(f"✅ Загружено {self.row_count:,} строк в staging")
        
    def step2_normalize(self):
        """Шаг 2: Нормализация staging → 3NF."""
        print("\n🏗️ Шаг 2: Нормализация (3NF)...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, это похоже на Online Retail или generic
        cursor.execute("PRAGMA table_info(staging)")
        cols = [c[1].lower() for c in cursor.fetchall()]
        
        if 'invoiceno' in cols and 'customerid' in cols:
            self._normalize_retail(cursor)
        else:
            self._normalize_generic(cursor, cols)
        
        conn.commit()
        conn.close()
        print("✅ Нормализация завершена")
        
    def _normalize_retail(self, cursor):
        """Нормализация для Online Retail."""
        cursor.executescript("""
            DROP TABLE IF EXISTS dim_countries;
            DROP TABLE IF EXISTS dim_customers;
            DROP TABLE IF EXISTS dim_products;
            DROP TABLE IF EXISTS fact_orders;
            DROP TABLE IF EXISTS fact_order_items;
            
            -- Справочник стран
            CREATE TABLE dim_countries AS
            SELECT DISTINCT Country as country_name, ROW_NUMBER() OVER () as country_id
            FROM staging WHERE Country IS NOT NULL;
            
            -- Клиенты
            CREATE TABLE dim_customers AS
            SELECT DISTINCT 
                CAST(CustomerID AS INTEGER) as customer_id,
                dc.country_id,
                MIN(InvoiceDate) as first_purchase,
                MAX(InvoiceDate) as last_purchase
            FROM staging s
            JOIN dim_countries dc ON s.Country = dc.country_name
            WHERE CustomerID IS NOT NULL
            GROUP BY CAST(CustomerID AS INTEGER), dc.country_id;
            
            -- Продукты
            CREATE TABLE dim_products AS
            SELECT DISTINCT StockCode as stock_code, Description as description
            FROM staging WHERE StockCode IS NOT NULL;
            
            -- Факт-таблица заказов
            CREATE TABLE fact_orders AS
            SELECT DISTINCT 
                InvoiceNo as invoice_no,
                CAST(CustomerID AS INTEGER) as customer_id,
                InvoiceDate as order_date
            FROM staging WHERE CustomerID IS NOT NULL;
            
            -- Факт-таблица строк заказов
            CREATE TABLE fact_order_items AS
            SELECT 
                InvoiceNo as invoice_no,
                StockCode as stock_code,
                CAST(Quantity AS INTEGER) as quantity,
                CAST(UnitPrice AS REAL) as unit_price,
                CAST(Quantity AS INTEGER) * CAST(UnitPrice AS REAL) as line_total
            FROM staging;
        """)
        
    def _normalize_generic(self, cursor, cols):
        """Универсальная нормализация."""
        cursor.execute("DROP TABLE IF EXISTS dim_data")
        col_defs = ', '.join([f'"{c}" TEXT' for c in cols])
        col_names = ', '.join([f'"{c}"' for c in cols])
        cursor.execute(f"CREATE TABLE dim_data AS SELECT {col_names} FROM staging")
        
    def step3_create_mart(self):
        """Шаг 3: Создаём аналитическую витрину."""
        print("\n📊 Шаг 3: Создание аналитической витрины...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Проверяем, что создалось
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        if 'fact_orders' in tables:
            # Витрина для Retail
            cursor.executescript("""
                DROP VIEW IF EXISTS mart_sales;
                CREATE VIEW mart_sales AS
                SELECT 
                    fo.invoice_no,
                    fo.order_date,
                    fo.customer_id,
                    dc.country_name,
                    foi.stock_code,
                    dp.description,
                    foi.quantity,
                    foi.unit_price,
                    foi.line_total,
                    strftime('%Y-%m', fo.order_date) as month,
                    strftime('%Y', fo.order_date) as year
                FROM fact_orders fo
                JOIN fact_order_items foi ON fo.invoice_no = foi.invoice_no
                JOIN dim_customers dcust ON fo.customer_id = dcust.customer_id
                JOIN dim_countries dc ON dcust.country_id = dc.country_id
                JOIN dim_products dp ON foi.stock_code = dp.stock_code;
            """)
            print("✅ Витрина mart_sales создана (Retail)")
        else:
            cursor.execute("DROP VIEW IF EXISTS mart_data")
            cursor.execute("CREATE VIEW mart_data AS SELECT * FROM dim_data")
            print("✅ Витрина mart_data создана (Generic)")
        
        conn.commit()
        conn.close()
        
    def step4_analyze(self):
        """Шаг 4: SQL-аналитика."""
        print("\n🔍 Шаг 4: SQL-аналитика...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        insights = []
        
        # Проверяем, какая витрина доступна
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = [v[0] for v in cursor.fetchall()]
        
        if 'mart_sales' in views:
            # Аналитика для Retail
            queries = [
                ("Всего записей", "SELECT COUNT(*) FROM mart_sales"),
                ("Выручка", "SELECT ROUND(SUM(line_total), 2) FROM mart_sales"),
                ("Уникальных клиентов", "SELECT COUNT(DISTINCT customer_id) FROM mart_sales"),
                ("Уникальных товаров", "SELECT COUNT(DISTINCT stock_code) FROM mart_sales"),
                ("Топ-страна", "SELECT country_name, ROUND(SUM(line_total), 2) as rev FROM mart_sales GROUP BY country_name ORDER BY rev DESC LIMIT 1"),
            ]
            
            for name, sql in queries:
                try:
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    insights.append(f"{name}: {result[0]}")
                except Exception as e:
                    insights.append(f"{name}: ошибка ({str(e)[:30]})")
        else:
            insights.append("Generic CSV loaded — basic schema only")
        
        conn.close()
        print("✅ Аналитика выполнена")
        return insights
        
    def step5_visualize(self):
        """Шаг 5: Генерация дашборда."""
        print("\n🎨 Шаг 5: Визуализация...")
        
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import pandas as pd
        
        png_path = self.output_dir / 'dashboard_etl.png'
        conn = sqlite3.connect(self.db_path)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('ETL Pipeline Dashboard', fontsize=18, fontweight='bold', color='#1E2761')
        fig.patch.set_facecolor('#f5f7fa')
        
        try:
            # Проверяем доступные таблицы
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = [v[0] for v in cursor.fetchall()]
            
            if 'mart_sales' in views:
                # Динамика по месяцам
                q1 = "SELECT month, ROUND(SUM(line_total), 2) as revenue FROM mart_sales GROUP BY month ORDER BY month"
                df1 = pd.read_sql_query(q1, conn)
                if not df1.empty:
                    axes[0, 0].plot(df1['month'], df1['revenue'], marker='o', color='#4a90e2')
                    axes[0, 0].set_title('Выручка по месяцам', fontsize=12)
                    axes[0, 0].tick_params(axis='x', rotation=30)
                
                # Топ-5 стран
                q2 = "SELECT country_name, ROUND(SUM(line_total), 2) as revenue FROM mart_sales GROUP BY country_name ORDER BY revenue DESC LIMIT 5"
                df2 = pd.read_sql_query(q2, conn)
                if not df2.empty:
                    axes[0, 1].pie(df2['revenue'], labels=df2['country_name'], autopct='%1.0f%%')
                    axes[0, 1].set_title('Топ-5 стран', fontsize=12)
                
                # Топ-5 товаров
                q3 = "SELECT description, SUM(quantity) as qty FROM mart_sales GROUP BY description ORDER BY qty DESC LIMIT 5"
                df3 = pd.read_sql_query(q3, conn)
                if not df3.empty:
                    axes[1, 0].barh(df3['description'], df3['qty'], color='#28a745')
                    axes[1, 0].set_title('Топ-5 товаров (шт.)', fontsize=12)
                    axes[1, 0].invert_yaxis()
                
                # ARPU
                q4 = "SELECT month, ROUND(SUM(line_total)/COUNT(DISTINCT customer_id), 2) as arpu FROM mart_sales GROUP BY month ORDER BY month"
                df4 = pd.read_sql_query(q4, conn)
                if not df4.empty:
                    axes[1, 1].bar(df4['month'], df4['arpu'], color='#ffc107')
                    axes[1, 1].set_title('ARPU по месяцам', fontsize=12)
                    axes[1, 1].tick_params(axis='x', rotation=30)
        except Exception as e:
            axes[0, 0].text(0.5, 0.5, f'Visualization error:\n{str(e)[:50]}', ha='center', va='center')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(png_path, dpi=150, bbox_inches='tight', facecolor='#f5f7fa')
        plt.close()
        conn.close()
        
        print(f"✅ Дашборд сохранён: {png_path}")
        return png_path
        
    def step6_generate_pdf(self, insights, png_path):
        """Шаг 6: Генерация PDF-отчёта."""
        print("\n📄 Шаг 6: Генерация PDF...")
        
        pdf_path = self.output_dir / f'etl_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        c = canvas.Canvas(str(pdf_path), pagesize=landscape(A4))
        
        # Титул
        c.setFillColor(NAVY)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(ICE)
        c.rect(0, H-8, W, 8, fill=1, stroke=0)
        c.rect(0, 0, W, 8, fill=1, stroke=0)
        c.setFillColor(HexColor('#ffffff'))
        c.setFont(FONT_B, 42)
        c.drawCentredString(W/2, H/2+30, "ETL Pipeline Report")
        c.setFont(FONT, 20)
        c.drawCentredString(W/2, H/2-20, f"CSV → SQLite → Data Mart → Dashboard")
        c.setFont(FONT, 14)
        c.drawCentredString(W/2, H/2-60, f"Файл: {self.csv_path.name} | Записей: {self.row_count:,}")
        c.setFont(FONT, 12)
        c.drawCentredString(W/2, 80, f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        c.showPage()
        
        # Инсайты
        c.setFillColor(LIGHT)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(NAVY)
        c.setFont(FONT_B, 28)
        c.drawString(50, H-50, "Ключевые метрики")
        c.setFillColor(ACCENT)
        c.rect(50, H-62, 150, 3, fill=1, stroke=0)
        
        y = H - 100
        c.setFillColor(DARK)
        c.setFont(FONT, 16)
        for insight in insights:
            c.drawString(50, y, f"• {insight}")
            y -= 28
        
        # Дашборд
        if png_path.exists():
            c.drawImage(str(png_path), 50, 80, width=W-100, height=H-200, preserveAspectRatio=True, mask='auto')
        
        c.showPage()
        c.save()
        
        print(f"✅ PDF сохранён: {pdf_path}")
        return pdf_path


def main():
    parser = argparse.ArgumentParser(description='ETL Pipeline: CSV → SQLite → Report')
    parser.add_argument('--input', required=True, help='Путь к CSV файлу')
    parser.add_argument('--output-dir', default='./etl_output', help='Директория выхода')
    args = parser.parse_args()
    
    pipeline = ETLPipeline(args.input, args.output_dir)
    pipeline.run()


if __name__ == "__main__":
    main()
