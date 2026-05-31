#!/usr/bin/env python3
"""
generate_data.py — генератор синтетических датасетов для портфолио Data Analyst.
Запуск: python3 generate_data.py
Требования: Python 3.8+ (без внешних зависимостей — только стандартная библиотека)
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

def generate_funnel():
    """Проект 1: E-commerce Funnel — 5000 пользователей, 30 дней."""
    n_users = 5000
    channels = ['organic', 'paid_social', 'search', 'email', 'referral']
    channel_weights = [0.30, 0.25, 0.20, 0.15, 0.10]
    devices = ['mobile', 'desktop', 'tablet']
    device_weights = [0.55, 0.35, 0.10]
    prices = [29, 49, 99, 149, 199, 299, 499]
    price_weights = [0.15, 0.20, 0.25, 0.15, 0.10, 0.10, 0.05]

    start_date = datetime(2026, 5, 1)
    dates = [start_date + timedelta(days=i) for i in range(30)]

    users = []
    for uid in range(1, n_users + 1):
        reg_date = random.choice(dates)
        channel = random.choices(channels, channel_weights)[0]
        device = random.choices(devices, device_weights)[0]
        users.append({
            'user_id': uid,
            'registration_date': reg_date.strftime('%Y-%m-%d'),
            'channel': channel,
            'device': device
        })

    events = []
    for u in users:
        reg = datetime.strptime(u['registration_date'], '%Y-%m-%d')
        # View product: 80%
        if random.random() < 0.80:
            view_dt = reg + timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
            events.append({
                'user_id': u['user_id'],
                'event_type': 'view_product',
                'event_date': view_dt.strftime('%Y-%m-%d %H:%M:%S'),
                'channel': u['channel'],
                'device': u['device'],
                'revenue': 0
            })
            # Add to cart: 40% of viewers
            if random.random() < 0.40:
                cart_dt = view_dt + timedelta(hours=random.randint(1, 48))
                events.append({
                    'user_id': u['user_id'],
                    'event_type': 'add_to_cart',
                    'event_date': cart_dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'channel': u['channel'],
                    'device': u['device'],
                    'revenue': 0
                })
                # Purchase: 25% of cart-adders
                if random.random() < 0.25:
                    purchase_dt = cart_dt + timedelta(hours=random.randint(1, 72))
                    revenue = random.choices(prices, price_weights)[0]
                    events.append({
                        'user_id': u['user_id'],
                        'event_type': 'purchase',
                        'event_date': purchase_dt.strftime('%Y-%m-%d %H:%M:%S'),
                        'channel': u['channel'],
                        'device': u['device'],
                        'revenue': revenue
                    })

    with open('01-ecommerce-funnel/funnel_events.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'event_type', 'event_date', 'channel', 'device', 'revenue'])
        writer.writeheader()
        writer.writerows(events)

    total_rev = sum(e['revenue'] for e in events)
    purchasers = len(set(e['user_id'] for e in events if e['event_type'] == 'purchase'))
    print(f"[Funnel] Events: {len(events):,} | Revenue: ${total_rev:,} | Buyers: {purchasers}")
    return events

def generate_ab_test():
    """Проект 2: A/B Test — 10,000 пользователей, 2 недели."""
    n = 10000
    variants = ['A'] * (n // 2) + ['B'] * (n // 2)
    random.shuffle(variants)

    start = datetime(2026, 5, 1)
    records = []
    for i in range(n):
        variant = variants[i]
        reg_date = start + timedelta(minutes=i)
        # A = 12% conversion, B = 14.5% conversion (lift ~20%)
        converted = random.random() < (0.12 if variant == 'A' else 0.145)
        revenue = 0
        if converted:
            revenue = random.choices([29, 49, 99, 149, 199], [0.2, 0.3, 0.25, 0.15, 0.1])[0]
        records.append({
            'user_id': i + 1,
            'variant': variant,
            'registration_date': reg_date.strftime('%Y-%m-%d %H:%M:%S'),
            'converted': 1 if converted else 0,
            'revenue': revenue
        })

    with open('02-ab-test-analysis/ab_test_results.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['user_id', 'variant', 'registration_date', 'converted', 'revenue'])
        writer.writeheader()
        writer.writerows(records)

    conv_a = sum(1 for r in records if r['variant'] == 'A' and r['converted']) / (n // 2)
    conv_b = sum(1 for r in records if r['variant'] == 'B' and r['converted']) / (n // 2)
    print(f"[A/B] A conv: {conv_a:.3%} | B conv: {conv_b:.3%} | Lift: {(conv_b/conv_a - 1):.1%}")
    return records

def generate_churn():
    """Проект 3: Churn Prediction — 3,000 пользователей SaaS."""
    n = 3000
    plans = ['free', 'basic', 'pro', 'enterprise']
    plan_weights = [0.4, 0.3, 0.2, 0.1]

    records = []
    start = datetime(2026, 1, 1)
    for i in range(n):
        signup = start + timedelta(days=random.randint(0, 90))
        age = random.randint(18, 65)
        plan = random.choices(plans, plan_weights)[0]
        sessions = max(0, random.gauss(8, 4))
        avg_session = max(1, random.gauss(12, 5))
        tickets = max(0, int(random.gauss(0.5, 1)))
        days_last_login = max(0, random.gauss(7, 7))
        pay_failures = max(0, int(random.gauss(0.2, 0.5)))

        # Churn score based on features
        score = 0.0
        if plan == 'free': score += 0.30
        if plan == 'basic': score += 0.15
        if sessions < 3: score += 0.25
        if days_last_login > 14: score += 0.35
        if tickets > 2: score += 0.15
        if pay_failures > 0: score += 0.20

        churned = 1 if random.random() < score else 0
        records.append({
            'user_id': i + 1,
            'signup_date': signup.strftime('%Y-%m-%d'),
            'age': age,
            'plan': plan,
            'monthly_sessions': round(sessions, 1),
            'avg_session_min': round(avg_session, 1),
            'support_tickets': tickets,
            'days_since_last_login': round(days_last_login, 1),
            'payment_failures': pay_failures,
            'churned': churned
        })

    with open('03-churn-prediction/churn_dataset.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'user_id', 'signup_date', 'age', 'plan', 'monthly_sessions',
            'avg_session_min', 'support_tickets', 'days_since_last_login',
            'payment_failures', 'churned'
        ])
        writer.writeheader()
        writer.writerows(records)

    churn_rate = sum(r['churned'] for r in records) / n
    print(f"[Churn] Records: {n:,} | Churn rate: {churn_rate:.1%}")
    return records

if __name__ == '__main__':
    import os
    os.makedirs('01-ecommerce-funnel', exist_ok=True)
    os.makedirs('02-ab-test-analysis', exist_ok=True)
    os.makedirs('03-churn-prediction', exist_ok=True)

    print("=== Генерация датасетов ===")
    generate_funnel()
    generate_ab_test()
    generate_churn()
    print("=== Готово ===")
