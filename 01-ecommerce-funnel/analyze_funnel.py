#!/usr/bin/env python3
"""
analyze_funnel.py — анализ воронки продаж на чистом Python.
Запуск: python3 analyze_funnel.py
"""

import csv
from collections import defaultdict, Counter

def load_data(filepath):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def analyze(events):
    # Шаг 1: Группировка по пользователям
    users = defaultdict(lambda: {'viewed': False, 'carted': False, 'purchased': False, 'revenue': 0, 'channel': '', 'device': ''})
    for row in events:
        uid = int(row['user_id'])
        etype = row['event_type']
        if etype == 'view_product':
            users[uid]['viewed'] = True
            users[uid]['channel'] = row['channel']
            users[uid]['device'] = row['device']
        elif etype == 'add_to_cart':
            users[uid]['carted'] = True
        elif etype == 'purchase':
            users[uid]['purchased'] = True
            users[uid]['revenue'] += int(row['revenue'])

    total = len(users)
    viewed = sum(1 for u in users.values() if u['viewed'])
    carted = sum(1 for u in users.values() if u['carted'])
    purchased = sum(1 for u in users.values() if u['purchased'])
    total_revenue = sum(u['revenue'] for u in users.values())

    print("=" * 50)
    print("📊 ВОРОНКА ПРОДАЖ")
    print("=" * 50)
    print(f"Всего пользователей:     {total:,}")
    print(f"Просмотрели товар:     {viewed:,} ({viewed/total:.1%})")
    print(f"Добавили в корзину:    {carted:,} ({carted/viewed:.1%} от просмотревших)")
    print(f"Совершили покупку:     {purchased:,} ({purchased/carted:.1%} от добавивших, {purchased/total:.1%} от всех)")
    print(f"Общая выручка:         ${total_revenue:,}")
    print(f"Средний чек:           ${total_revenue/max(purchased,1):.0f}")
    print(f"ARPU (выручка/всех):   ${total_revenue/total:.2f}")

    # Анализ по каналам
    print("\n📡 КОНВЕРСИЯ ПО КАНАЛАМ")
    print("-" * 50)
    channels = defaultdict(lambda: {'total': 0, 'viewed': 0, 'purchased': 0, 'revenue': 0})
    for uid, u in users.items():
        ch = u['channel']
        channels[ch]['total'] += 1
        if u['viewed']: channels[ch]['viewed'] += 1
        if u['purchased']: channels[ch]['purchased'] += 1
        channels[ch]['revenue'] += u['revenue']

    for ch in sorted(channels, key=lambda x: channels[x]['purchased']/channels[x]['total'], reverse=True):
        data = channels[ch]
        conv = data['purchased'] / data['total']
        print(f"{ch:12} | Всего: {data['total']:4} | Покупатели: {data['purchased']:3} | Конверсия: {conv:.1%} | Выручка: ${data['revenue']:,}")

    # Анализ по устройствам
    print("\n📱 КОНВЕРСИЯ ПО УСТРОЙСТВАМ")
    print("-" * 50)
    devices = defaultdict(lambda: {'total': 0, 'purchased': 0, 'revenue': 0})
    for uid, u in users.items():
        d = u['device']
        devices[d]['total'] += 1
        if u['purchased']: devices[d]['purchased'] += 1
        devices[d]['revenue'] += u['revenue']

    for d in sorted(devices, key=lambda x: devices[x]['purchased']/devices[x]['total'], reverse=True):
        data = devices[d]
        conv = data['purchased'] / data['total']
        print(f"{d:10} | Всего: {data['total']:4} | Покупатели: {data['purchased']:3} | Конверсия: {conv:.1%} | Выручка: ${data['revenue']:,}")

    # Время до покупки (упрощённо — среднее по дням)
    print("\n⏱️  ВРЕМЕННАЯ АНАЛИТИКА")
    print("-" * 50)
    from datetime import datetime
    purchase_times = []
    for row in events:
        if row['event_type'] == 'purchase':
            uid = int(row['user_id'])
            # Ищем дату регистрации (первое событие пользователя)
            reg_events = [e for e in events if int(e['user_id']) == uid]
            if reg_events:
                reg_date = datetime.strptime(reg_events[0]['event_date'], '%Y-%m-%d %H:%M:%S')
                pur_date = datetime.strptime(row['event_date'], '%Y-%m-%d %H:%M:%S')
                purchase_times.append((pur_date - reg_date).total_seconds() / 3600)
    if purchase_times:
        avg_hours = sum(purchase_times) / len(purchase_times)
        print(f"Среднее время от первого события до покупки: {avg_hours:.1f} часов")

    print("\n" + "=" * 50)
    print("💡 ИНСАЙТЫ ДЛЯ БИЗНЕСА")
    print("=" * 50)
    best_channel = max(channels, key=lambda x: channels[x]['purchased'])
    worst_device = min(devices, key=lambda x: devices[x]['purchased']/devices[x]['total'])
    print(f"• Лучший канал по конверсии: {best_channel}")
    print(f"• Устройство с проблемами: {worst_device} — проверить UX")
    print(f"• Воронка теряет {100*(1-purchased/carted):.0f}% на этапе 'корзина → покупка'")
    print(f"• Рекомендация: A/B тест email-напоминаний об abandoned cart")

if __name__ == '__main__':
    events = load_data('01-ecommerce-funnel/funnel_events.csv')
    analyze(events)
