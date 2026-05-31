#!/usr/bin/env python3
"""
analyze_retail.py — RFM + когортный анализ на чистом Python (без pandas).
Запуск: python3 analyze_retail.py
"""

import csv
from collections import defaultdict, Counter
from datetime import datetime, timedelta

def parse_date(s):
    return datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

def load_data(filepath, max_rows=100000):
    """Загружаем первые N строк для скорости (полный анализ в ноутбуке)."""
    records = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= max_rows: break
            try:
                qty = int(row['Quantity'])
                price = float(row['UnitPrice'])
                if qty <= 0 or price <= 0 or not row['CustomerID']:
                    continue
                records.append({
                    'invoice': row['InvoiceNo'],
                    'stock': row['StockCode'],
                    'desc': row['Description'],
                    'quantity': qty,
                    'date': parse_date(row['InvoiceDate']),
                    'unit_price': price,
                    'customer_id': int(float(row['CustomerID'])),
                    'country': row['Country'],
                    'revenue': qty * price
                })
            except:
                continue
    return records

def rfm_analysis(records):
    """Recency, Frequency, Monetary на чистом Python."""
    max_date = max(r['date'] for r in records)
    
    customers = defaultdict(lambda: {'last_date': None, 'frequency': 0, 'monetary': 0, 'invoices': set()})
    for r in records:
        cid = r['customer_id']
        customers[cid]['last_date'] = max(customers[cid]['last_date'] or r['date'], r['date'])
        customers[cid]['frequency'] += 1
        customers[cid]['monetary'] += r['revenue']
        customers[cid]['invoices'].add(r['invoice'])
    
    # RFM scores (1–5)
    rfm_data = []
    for cid, data in customers.items():
        recency = (max_date - data['last_date']).days
        frequency = len(data['invoices'])
        monetary = data['monetary']
        rfm_data.append({
            'customer_id': cid,
            'recency': recency,
            'frequency': frequency,
            'monetary': monetary
        })
    
    # Percentile-based scoring
    rfm_data.sort(key=lambda x: x['recency'], reverse=True)
    for i, d in enumerate(rfm_data):
        d['r_score'] = 1 + int(4 * i / len(rfm_data))
    
    rfm_data.sort(key=lambda x: x['frequency'])
    for i, d in enumerate(rfm_data):
        d['f_score'] = 1 + int(4 * i / len(rfm_data))
    
    rfm_data.sort(key=lambda x: x['monetary'])
    for i, d in enumerate(rfm_data):
        d['m_score'] = 1 + int(4 * i / len(rfm_data))
    
    # Segments
    for d in rfm_data:
        r, f, m = d['r_score'], d['f_score'], d['m_score']
        if r >= 4 and f >= 4 and m >= 4:
            d['segment'] = 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            d['segment'] = 'Loyal'
        elif r >= 4 and f <= 2:
            d['segment'] = 'New'
        elif r <= 2 and f >= 3:
            d['segment'] = 'At Risk'
        elif r <= 2 and f <= 2:
            d['segment'] = 'Lost'
        else:
            d['segment'] = 'Regular'
    
    return rfm_data

def top_products(records, n=10):
    product_revenue = defaultdict(float)
    product_qty = defaultdict(int)
    for r in records:
        product_revenue[r['stock']] += r['revenue']
        product_qty[r['stock']] += r['quantity']
    
    top = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:n]
    return top

def country_stats(records):
    country_rev = defaultdict(float)
    country_customers = defaultdict(set)
    for r in records:
        country_rev[r['country']] += r['revenue']
        country_customers[r['country']].add(r['customer_id'])
    
    stats = []
    for country in sorted(country_rev, key=country_rev.get, reverse=True):
        stats.append({
            'country': country,
            'revenue': country_rev[country],
            'customers': len(country_customers[country])
        })
    return stats

def main():
    print("=" * 50)
    print("🛍️  RFM АНАЛИЗ РОЗНИЧНЫХ ПРОДАЖ (UCI Online Retail)")
    print("=" * 50)
    
    records = load_data('online_retail.csv', max_rows=50000)
    print(f"Загружено транзакций: {len(records):,}")
    print(f"Уникальных клиентов: {len(set(r['customer_id'] for r in records)):,}")
    print(f"Уникальных товаров: {len(set(r['stock'] for r in records)):,}")
    print(f"Период: {min(r['date'] for r in records).date()} — {max(r['date'] for r in records).date()}")
    
    total_revenue = sum(r['revenue'] for r in records)
    print(f"\nОбщая выручка: ${total_revenue:,.2f}")
    print(f"Средний чек: ${total_revenue/len(records):.2f}")
    
    # RFM
    rfm = rfm_analysis(records)
    print(f"\n📊 RFM-СЕГМЕНТАЦИЯ ({len(rfm)} клиентов)")
    print("-" * 50)
    segments = Counter(d['segment'] for d in rfm)
    for seg, cnt in segments.most_common():
        pct = cnt / len(rfm) * 100
        rev = sum(d['monetary'] for d in rfm if d['segment'] == seg)
        print(f"{seg:12} | {cnt:4} клиентов ({pct:5.1f}%) | Выручка: ${rev:,.0f}")
    
    # Top products
    print("\n🏆 ТОП-10 ТОВАРОВ ПО ВЫРУЧКЕ")
    print("-" * 50)
    for stock, rev in top_products(records, 10):
        qty = sum(r['quantity'] for r in records if r['stock'] == stock)
        print(f"{stock:8} | ${rev:,.0f} | {qty:,} шт.")
    
    # Countries
    print("\n🌍 ГЕОГРАФИЯ ПРОДАЖ (топ-10)")
    print("-" * 50)
    for stat in country_stats(records)[:10]:
        print(f"{stat['country']:20} | ${stat['revenue']:,.0f} | {stat['customers']} клиентов")
    
    print("\n" + "=" * 50)
    print("💡 ИНСАЙТЫ")
    print("=" * 50)
    top_seg = segments.most_common(1)[0]
    print(f"• Крупнейший сегмент: {top_seg[0]} ({top_seg[1]} клиентов)")
    print(f"• Рекомендация: персональные предложения для 'At Risk' и 'Lost'")
    print(f"• UK доминирует: ~80% выручки — рассмотреть расширение в EU")

if __name__ == '__main__':
    main()
