#!/usr/bin/env python3
"""
dashboards.py — генерация интерактивных HTML-дашбордов для всех проектов.
Запуск: cd ~/projects/data-analyst-portfolio && uv run python3 dashboards.py
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import os

def generate_funnel_dashboard():
    """Дашборд 1: E-commerce Funnel"""
    df = pd.read_csv('01-ecommerce-funnel/funnel_events.csv')
    df['event_date'] = pd.to_datetime(df['event_date'])
    
    # Подготовка данных
    users = df.groupby('user_id').agg(
        channel=('channel', 'first'),
        device=('device', 'first'),
        viewed=('event_type', lambda x: (x == 'view_product').sum()),
        carted=('event_type', lambda x: (x == 'add_to_cart').sum()),
        purchased=('event_type', lambda x: (x == 'purchase').sum()),
        revenue=('revenue', 'sum')
    ).reset_index()
    
    # Воронка
    funnel_values = [
        len(users),
        users['viewed'].sum(),
        users['carted'].sum(),
        users['purchased'].sum()
    ]
    funnel_labels = ['Все пользователи', 'Просмотрели товар', 'Добавили в корзину', 'Совершили покупку']
    funnel_pcts = [100] + [funnel_values[i]/funnel_values[i-1]*100 for i in range(1, len(funnel_values))]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '🎯 Воронка продаж',
            '📡 Конверсия по каналам',
            '📱 Конверсия по устройствам',
            '💰 Выручка по каналам'
        ),
        specs=[[{"type": "funnel"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # Воронка
    fig.add_trace(go.Funnel(
        y=funnel_labels,
        x=funnel_values,
        textinfo="value+percent previous",
        marker=dict(color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c']),
        name='Воронка'
    ), row=1, col=1)
    
    # Каналы
    ch = users.groupby('channel').agg(
        total=('user_id', 'count'),
        buyers=('purchased', 'sum'),
        revenue=('revenue', 'sum')
    ).reset_index()
    ch['conv'] = ch['buyers'] / ch['total'] * 100
    ch = ch.sort_values('conv', ascending=True)
    
    fig.add_trace(go.Bar(
        x=ch['conv'], y=ch['channel'], orientation='h',
        marker_color='#2ecc71', name='Конверсия (%)',
        text=ch['conv'].round(1).astype(str) + '%',
        textposition='outside'
    ), row=1, col=2)
    
    # Устройства
    dev = users.groupby('device').agg(
        total=('user_id', 'count'),
        buyers=('purchased', 'sum')
    ).reset_index()
    dev['conv'] = dev['buyers'] / dev['total'] * 100
    
    fig.add_trace(go.Bar(
        x=dev['device'], y=dev['conv'],
        marker_color=['#e74c3c', '#f39c12', '#3498db'],
        name='Конверсия (%)',
        text=dev['conv'].round(1).astype(str) + '%',
        textposition='outside'
    ), row=2, col=1)
    
    # Выручка по каналам
    fig.add_trace(go.Bar(
        x=ch['channel'], y=ch['revenue'],
        marker_color='#3498db', name='Выручка ($)',
        text=ch['revenue'].round(0).astype(int).astype(str) + '$',
        textposition='outside'
    ), row=2, col=2)
    
    fig.update_layout(
        title_text="<b>🛒 Отчёт: E-commerce Funnel Analysis</b><br><sup>Анализ воронки, каналов и устройств</sup>",
        title_x=0.5,
        height=800,
        showlegend=False,
        template='plotly_white'
    )
    
    fig.write_html('01-ecommerce-funnel/dashboard.html', include_plotlyjs='cdn')
    print("✅ Дашборд 1 создан: 01-ecommerce-funnel/dashboard.html")

def generate_ab_dashboard():
    """Дашборд 2: A/B Test"""
    df = pd.read_csv('02-ab-test-analysis/ab_test_results.csv')
    
    summary = df.groupby('variant').agg(
        users=('user_id', 'count'),
        conversions=('converted', 'sum'),
        revenue=('revenue', 'sum')
    ).reset_index()
    summary['conversion_rate'] = summary['conversions'] / summary['users'] * 100
    summary['arpu'] = summary['revenue'] / summary['users']
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Конверсия по вариантам',
            'ARPU по вариантам',
            'Выручка по вариантам',
            'Статистическая значимость'
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "indicator"}]],
        vertical_spacing=0.15
    )
    
    colors = ['#3498db', '#e74c3c']
    
    fig.add_trace(go.Bar(
        x=summary['variant'], y=summary['conversion_rate'],
        marker_color=colors, name='Конверсия (%)',
        text=summary['conversion_rate'].round(2).astype(str) + '%',
        textposition='outside'
    ), row=1, col=1)
    
    fig.add_trace(go.Bar(
        x=summary['variant'], y=summary['arpu'],
        marker_color=colors, name='ARPU ($)',
        text='$' + summary['arpu'].round(2).astype(str),
        textposition='outside'
    ), row=1, col=2)
    
    fig.add_trace(go.Bar(
        x=summary['variant'], y=summary['revenue'],
        marker_color=colors, name='Выручка ($)',
        text='$' + summary['revenue'].round(0).astype(int).astype(str),
        textposition='outside'
    ), row=2, col=1)
    
    # Z-test результат
    a = df[df['variant'] == 'A']
    b = df[df['variant'] == 'B']
    conv_a = a['converted'].sum() / len(a)
    conv_b = b['converted'].sum() / len(b)
    p_pooled = (a['converted'].sum() + b['converted'].sum()) / (len(a) + len(b))
    se = np.sqrt(p_pooled * (1 - p_pooled) * (1/len(a) + 1/len(b)))
    z = (conv_b - conv_a) / se
    from math import erf
    p_value = 2 * (1 - 0.5 * (1 + erf(abs(z) / np.sqrt(2))))
    
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=conv_b * 100,
        delta={"reference": conv_a * 100, "relative": True, "valueformat": ".1%"},
        title={"text": f"Конверсия B vs A<br><span style='font-size:12px'>p-value: {p_value:.6f}</span>"},
        number={'suffix': '%', 'valueformat': '.2f'},
        domain={'row': 1, 'column': 1}
    ), row=2, col=2)
    
    fig.update_layout(
        title_text="<b>🧪 Отчёт: A/B Test Analysis</b><br><sup>Статистическая значимость и бизнес-выводы</sup>",
        title_x=0.5,
        height=800,
        showlegend=False,
        template='plotly_white'
    )
    
    fig.write_html('02-ab-test-analysis/dashboard.html', include_plotlyjs='cdn')
    print("✅ Дашборд 2 создан: 02-ab-test-analysis/dashboard.html")

def generate_churn_dashboard():
    """Дашборд 3: Churn Prediction"""
    df = pd.read_csv('03-churn-prediction/churn_dataset.csv')
    
    # Risk score
    def risk_score(row):
        s = 0
        if row['plan'] == 'free': s += 30
        if row['plan'] == 'basic': s += 15
        if row['monthly_sessions'] < 3: s += 25
        if row['days_since_last_login'] > 14: s += 35
        if row['support_tickets'] > 2: s += 15
        if row['payment_failures'] > 0: s += 20
        return s
    
    df['risk_score'] = df.apply(risk_score, axis=1)
    df['risk_segment'] = pd.cut(df['risk_score'], 
        bins=[0, 20, 40, 60, 1000], 
        labels=['Низкий', 'Средний', 'Высокий', 'Критический'])
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Отток по тарифам',
            'Отток по сегментам риска',
            'Корреляция признаков с оттоком',
            'Распределение Risk Score'
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "histogram"}]],
        vertical_spacing=0.15
    )
    
    # По тарифам
    plan = df.groupby('plan').agg(
        total=('user_id', 'count'),
        churned=('churned', 'sum')
    ).reset_index()
    plan['rate'] = plan['churned'] / plan['total'] * 100
    plan = plan.sort_values('rate', ascending=True)
    
    fig.add_trace(go.Bar(
        x=plan['rate'], y=plan['plan'], orientation='h',
        marker_color=['#2ecc71', '#3498db', '#f39c12', '#e74c3c'],
        name='Отток (%)',
        text=plan['rate'].round(1).astype(str) + '%',
        textposition='outside'
    ), row=1, col=1)
    
    # По сегментам риска
    seg = df.groupby('risk_segment').agg(
        total=('user_id', 'count'),
        churned=('churned', 'sum')
    ).reset_index()
    seg['rate'] = seg['churned'] / seg['total'] * 100
    
    fig.add_trace(go.Bar(
        x=seg['risk_segment'], y=seg['rate'],
        marker_color=['#2ecc71', '#f39c12', '#e74c3c', '#8e44ad'],
        name='Отток (%)',
        text=seg['rate'].round(1).astype(str) + '%',
        textposition='outside'
    ), row=1, col=2)
    
    # Корреляции
    numeric = ['age', 'monthly_sessions', 'avg_session_min', 
               'support_tickets', 'days_since_last_login', 'payment_failures']
    corrs = df[numeric + ['churned']].corr()['churned'].drop('churned').sort_values(ascending=False)
    colors = ['#e74c3c' if x > 0 else '#3498db' for x in corrs.values]
    
    fig.add_trace(go.Bar(
        x=corrs.values, y=corrs.index, orientation='h',
        marker_color=colors, name='Корреляция',
        text=corrs.values.round(3).astype(str),
        textposition='outside'
    ), row=2, col=1)
    
    # Distribution
    fig.add_trace(go.Histogram(
        x=df[df['churned'] == 0]['risk_score'],
        name='Активные',
        marker_color='#3498db',
        opacity=0.7,
        nbinsx=20
    ), row=2, col=2)
    fig.add_trace(go.Histogram(
        x=df[df['churned'] == 1]['risk_score'],
        name='Оттекшие',
        marker_color='#e74c3c',
        opacity=0.7,
        nbinsx=20
    ), row=2, col=2)
    
    fig.update_layout(
        title_text="<b>🔄 Отчёт: Churn Prediction & Risk Scoring</b><br><sup>Сегментация оттока и ключевые факторы</sup>",
        title_x=0.5,
        height=800,
        barmode='overlay',
        template='plotly_white'
    )
    
    fig.write_html('03-churn-prediction/dashboard.html', include_plotlyjs='cdn')
    print("✅ Дашборд 3 создан: 03-churn-prediction/dashboard.html")

def generate_retail_dashboard():
    """Дашборд 4: Retail RFM (реальные данные)"""
    df = pd.read_csv('04-retail-rfm-analysis/online_retail.csv')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['Revenue'] = df['Quantity'] * df['UnitPrice']
    
    max_date = df['InvoiceDate'].max() + timedelta(days=1)
    
    # RFM
    rfm = df.groupby('CustomerID').agg(
        Recency=('InvoiceDate', lambda x: (max_date - x.max()).days),
        Frequency=('InvoiceNo', 'nunique'),
        Monetary=('Revenue', 'sum')
    ).reset_index()
    
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1]).astype(int)
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5]).astype(int)
    
    def segment(row):
        r, f, m = row['R_Score'], row['F_Score'], row['M_Score']
        if r >= 4 and f >= 4 and m >= 4: return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3: return 'Loyal'
        elif r >= 4 and f <= 2: return 'New'
        elif r >= 3 and f >= 2: return 'Potential'
        elif r <= 2 and f >= 3: return 'At Risk'
        elif r <= 2 and f >= 2: return 'Cannot Lose'
        else: return 'Lost'
    
    rfm['Segment'] = rfm.apply(segment, axis=1)
    
    # Месячная динамика
    df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')
    monthly = df.groupby('YearMonth')['Revenue'].sum().reset_index()
    monthly['YearMonth'] = monthly['YearMonth'].astype(str)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'RFM-сегменты: клиенты',
            'RFM-сегменты: выручка',
            'Динамика выручки по месяцам',
            'География продаж (топ-10 без UK)'
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "scatter"}, {"type": "bar"}]],
        vertical_spacing=0.15
    )
    
    seg_summary = rfm.groupby('Segment').agg(
        Count=('CustomerID', 'count'),
        TotalMonetary=('Monetary', 'sum')
    ).reset_index().sort_values('Count', ascending=True)
    
    colors = px.colors.qualitative.Set3[:len(seg_summary)]
    
    fig.add_trace(go.Bar(
        x=seg_summary['Count'], y=seg_summary['Segment'], orientation='h',
        marker_color=colors, name='Клиенты',
        text=seg_summary['Count'].astype(str),
        textposition='outside'
    ), row=1, col=1)
    
    fig.add_trace(go.Bar(
        x=seg_summary['TotalMonetary'], y=seg_summary['Segment'], orientation='h',
        marker_color=colors, name='Выручка',
        text='$' + (seg_summary['TotalMonetary']/1000).round(0).astype(int).astype(str) + 'K',
        textposition='outside'
    ), row=1, col=2)
    
    fig.add_trace(go.Scatter(
        x=monthly['YearMonth'], y=monthly['Revenue'],
        mode='lines+markers+text',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8),
        text=(monthly['Revenue']/1000).round(0).astype(int).astype(str) + 'K',
        textposition='top center',
        name='Выручка'
    ), row=2, col=1)
    
    # География
    geo = df.groupby('Country')['Revenue'].sum().reset_index().sort_values('Revenue', ascending=False)
    geo_no_uk = geo[geo['Country'] != 'United Kingdom'].head(10).sort_values('Revenue', ascending=True)
    
    fig.add_trace(go.Bar(
        x=geo_no_uk['Revenue'], y=geo_no_uk['Country'], orientation='h',
        marker_color='#2ecc71', name='Выручка',
        text='$' + geo_no_uk['Revenue'].round(0).astype(int).astype(str),
        textposition='outside'
    ), row=2, col=2)
    
    fig.update_layout(
        title_text="<b>🛍️ Отчёт: RFM & Cohort Analysis — Real Retail Data</b><br><sup>144K транзакций, 2,708 клиентов, 38 стран</sup>",
        title_x=0.5,
        height=900,
        showlegend=False,
        template='plotly_white'
    )
    
    fig.write_html('04-retail-rfm-analysis/dashboard.html', include_plotlyjs='cdn')
    print("✅ Дашборд 4 создан: 04-retail-rfm-analysis/dashboard.html")

if __name__ == '__main__':
    os.chdir('/home/clawd/projects/data-analyst-portfolio')
    print("=== Генерация интерактивных дашбордов ===")
    generate_funnel_dashboard()
    generate_ab_dashboard()
    generate_churn_dashboard()
    generate_retail_dashboard()
    print("\n🎉 Все дашборды готовы! Откройте .html файлы в браузере.")
