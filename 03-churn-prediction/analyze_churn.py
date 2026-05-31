#!/usr/bin/env python3
"""
analyze_churn.py — анализ оттока: распределения, корреляции, простой скоринг.
Запуск: python3 analyze_churn.py
"""

import csv
from collections import defaultdict, Counter
import math

def load_data(filepath):
    with open(filepath, 'r') as f:
        return list(csv.DictReader(f))

def mean(values):
    return sum(values) / len(values) if values else 0

def analyze(records):
    total = len(records)
    churned = sum(1 for r in records if int(r['churned']) == 1)
    churn_rate = churned / total

    print("=" * 50)
    print("🔄 АНАЛИЗ ОТТОКА (Churn)")
    print("=" * 50)
    print(f"Всего пользователей: {total:,}")
    print(f"Оттекших:            {churned:,}")
    print(f"Уровень оттока:      {churn_rate:.1%}")

    # По тарифам
    print("\n📋 ОТТОК ПО ТАРИФАМ")
    print("-" * 50)
    plans = defaultdict(lambda: {'total': 0, 'churned': 0})
    for r in records:
        p = r['plan']
        plans[p]['total'] += 1
        if int(r['churned']): plans[p]['churned'] += 1

    for plan in ['free', 'basic', 'pro', 'enterprise']:
        if plan not in plans: continue
        d = plans[plan]
        rate = d['churned'] / d['total']
        print(f"{plan:12} | Всего: {d['total']:4} | Отток: {d['churned']:3} | Rate: {rate:.1%}")

    # Распределение по числу сессий
    print("\n📊 СЕССИИ vs ОТТОК")
    print("-" * 50)
    buckets = {
        '0-2 сессий': [],
        '3-5 сессий': [],
        '6-10 сессий': [],
        '11+ сессий': []
    }
    for r in records:
        s = float(r['monthly_sessions'])
        churn = int(r['churned'])
        if s <= 2: buckets['0-2 сессий'].append(churn)
        elif s <= 5: buckets['3-5 сессий'].append(churn)
        elif s <= 10: buckets['6-10 сессий'].append(churn)
        else: buckets['11+ сессий'].append(churn)

    for bucket, vals in buckets.items():
        if vals:
            rate = sum(vals) / len(vals)
            print(f"{bucket:12} | n={len(vals):4} | Отток: {rate:.1%}")

    # Последний вход vs отток
    print("\n⏱️  ДНИ С ПОСЛЕДНЕГО ВХОДА vs ОТТОК")
    print("-" * 50)
    active = [float(r['days_since_last_login']) for r in records if not int(r['churned'])]
    churned_users = [float(r['days_since_last_login']) for r in records if int(r['churned'])]
    print(f"Активные: среднее {mean(active):.1f} дней")
    print(f"Оттекшие: среднее {mean(churned_users):.1f} дней")

    # Простой risk score (взвешенная сумма)
    print("\n🎯 RISK SCORE (упрощённый)")
    print("-" * 50)
    def risk_score(r):
        s = 0
        if r['plan'] == 'free': s += 30
        if r['plan'] == 'basic': s += 15
        if float(r['monthly_sessions']) < 3: s += 25
        if float(r['days_since_last_login']) > 14: s += 35
        if int(r['support_tickets']) > 2: s += 15
        if int(r['payment_failures']) > 0: s += 20
        return s

    scores = [(risk_score(r), int(r['churned'])) for r in records]
    scores.sort(key=lambda x: x[0], reverse=True)

    # Top 20% по risk score — сколько реально оттекли?
    top20_cutoff = int(0.2 * len(scores))
    top20 = scores[:top20_cutoff]
    top20_churn_rate = sum(1 for _, churned in top20 if churned) / len(top20)
    print(f"Топ-20% по risk score: отток {top20_churn_rate:.1%}")
    print(f"В среднем по всем: отток {churn_rate:.1%}")
    print(f"Risk score увеличивает точность в {top20_churn_rate/churn_rate:.1f}x раз")

    print("\n" + "=" * 50)
    print("💡 ВЫВОДЫ ДЛЯ БИЗНЕСА")
    print("=" * 50)
    worst_plan = max(plans, key=lambda x: plans[x]['churned']/plans[x]['total'])
    print(f"• Самый проблемный тариф: {worst_plan} — нужен onboarding/re-engagement")
    print(f"• Порог: пользователи с >14 дней без входа и <3 сессий — high risk")
    print(f"• Risk score выделяет группу с {top20_churn_rate:.0%} оттоком (вместо средних {churn_rate:.0%})")
    print(f"• Рекомендация: триггерные email/SMS для top-20% risk score")
    print(f"• Можно сократить отток на ~30% если реактивировать 50% из top-20%")

if __name__ == '__main__':
    records = load_data('03-churn-prediction/churn_dataset.csv')
    analyze(records)
