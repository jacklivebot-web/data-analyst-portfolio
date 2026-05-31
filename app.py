#!/usr/bin/env python3
"""
Streamlit-приложение: интерактивный дашборд портфолио.
Запуск: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Data Analyst Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
    <style>
    .main { background: #f0fdf4; }
    .stButton>button { 
        background: #059669 !important; 
        color: white !important;
        border-radius: 8px !important;
    }
    .stMetric { background: white; border-radius: 8px; padding: 10px; }
    h1 { color: #059669 !important; }
    h2 { color: #047857 !important; }
    </style>
""", unsafe_allow_html=True)

# Заголовок
st.title("📊 Портфолио Data Analyst")
st.markdown("### 7 production-ready проектов с интерактивными дашбордами")

# Боковое меню
project = st.sidebar.selectbox(
    "Выберите проект:",
    [
        "🏠 Главная",
        "🛒 Воронка e-commerce", 
        "🧪 A/B-тестирование",
        "🔄 Прогноз оттока",
        "🛍️ RFM-сегментация",
        "🗄️ SQL-аналитика",
        "⚡ ETL-пайплайн",
        "🔥 Продвинутый SQL"
    ]
)

if project == "🏠 Главная":
    st.header("Обзор портфолио")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Проектов", "7", "+3 SQL")
    col2.metric("SQL-запросов", "20+", "оконные функции")
    col3.metric("Строк данных", "144K", "реальные")
    col4.metric("Воспроизводимость", "100%", "Git + код")
    
    st.markdown("---")
    st.subheader("📈 Проекты")
    
    projects_data = [
        {"Номер": 1, "Проект": "Воронка e-commerce", "Ключевой вопрос": "Где теряются покупатели?", "Статус": "✅"},
        {"Номер": 2, "Проект": "A/B-тестирование", "Ключевой вопрос": "Вариант B лучше A?", "Статус": "✅"},
        {"Номер": 3, "Проект": "Прогноз оттока", "Ключевой вопрос": "Кто уйдёт?", "Статус": "✅"},
        {"Номер": 4, "Проект": "RFM-сегментация", "Ключевой вопрос": "Кто самые ценные?", "Статус": "✅"},
        {"Номер": 5, "Проект": "SQL-аналитика", "Ключевой вопрос": "Может ли SQL всё?", "Статус": "✅"},
        {"Номер": 6, "Проект": "ETL-пайплайн", "Ключевой вопрос": "Можно ли автоматизировать?", "Статус": "✅"},
        {"Номер": 7, "Проект": "Продвинутый SQL", "Ключевой вопрос": "Что покажут оконные функции?", "Статус": "✅"},
    ]
    df_projects = pd.DataFrame(projects_data)
    st.dataframe(df_projects, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("🛠️ Технологический стек")
    techs = ["Python", "pandas", "numpy", "matplotlib", "SQLite", "scikit-learn", "scipy", "Jupyter", "Git", "Linux"]
    st.write(" • ".join(techs))

elif project == "🛒 Воронка e-commerce":
    st.header("🛒 Воронка e-commerce")
    st.markdown("**Вопрос:** Где теряются покупатели на пути к заказу?")
    
    # Симуляция данных
    stages = ['View', 'Cart', 'Checkout', 'Purchase']
    values = [100, 40, 25, 21]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Конверсия", "2.1%", "потенциал 8.5%")
        st.metric("Главная потеря", "65%", "уходят после корзины")
    with col2:
        st.metric("Mobile", "9.2%", "vs Desktop 11.0%")
        st.metric("Лучший канал", "Referral", "11.5% конверсия")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#059669', '#34d399', '#6ee7b7', '#a7f3d0']
    bars = ax.barh(stages, values, color=colors)
    ax.set_xlabel('Конверсия (%)')
    ax.set_title('Воронка конверсии', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    for bar, val in zip(bars, values):
        ax.text(val + 1, bar.get_y() + bar.get_height()/2, f'{val}%', va='center')
    st.pyplot(fig)
    
    st.markdown("**Решение:** Упростить mobile-checkout, проверить аудиторию paid social.")

elif project == "🧪 A/B-тестирование":
    st.header("🧪 A/B-тестирование")
    st.markdown("**Вопрос:** Вариант B статистически лучше A?")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Конверсия A", "12.26%")
    col2.metric("Конверсия B", "15.28%", "+24.6%")
    col3.metric("p-value", "<0.0001", "99% доверие")
    
    # График
    fig, ax = plt.subplots(figsize=(8, 5))
    variants = ['Вариант A', 'Вариант B']
    conv = [12.26, 15.28]
    colors = ['#9ca3af', '#059669']
    bars = ax.bar(variants, conv, color=colors, width=0.5)
    ax.set_ylabel('Конверсия (%)')
    ax.set_title('A/B Test Results', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 20)
    for bar, val in zip(bars, conv):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.3, f'{val}%', ha='center', fontweight='bold')
    st.pyplot(fig)
    
    st.metric("ARPU", "$10.40 → $13.31", "+28%")
    st.markdown("**Решение:** Раскатить вариант B на 100% трафика.")

elif project == "🔄 Прогноз оттока":
    st.header("🔄 Прогноз оттока")
    st.markdown("**Вопрос:** Кто уйдёт в следующем месяце?")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Точность модели", "87.2%", "ROC-AUC")
    col2.metric("High-risk отток", "53.5%", "топ-20%")
    col3.metric("Free-plan отток", "37.8%", "сегмент")
    
    # Симуляция рисков
    st.subheader("🎯 Risk Score Distribution")
    risk_scores = [15, 25, 35, 45, 55, 65, 75, 85]
    churn_rates = [5, 8, 12, 18, 25, 38, 55, 72]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(risk_scores, churn_rates, marker='o', color='#059669', linewidth=2, markersize=8)
    ax.fill_between(risk_scores, churn_rates, alpha=0.2, color='#059669')
    ax.set_xlabel('Risk Score')
    ax.set_ylabel('Churn Rate (%)')
    ax.set_title('Зависимость оттока от Risk Score', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    st.markdown("**Решение:** Триггерные кампании для high-risk сегмента.")

elif project == "🛍️ RFM-сегментация":
    st.header("🛍️ RFM-сегментация")
    st.markdown("*Реальные данные: 144K транзакций, 2,708 клиентов*")
    
    segments = ['Champions', 'Loyal', 'Potential', 'New', 'At Risk', 'Lost']
    counts = [266, 297, 350, 220, 266, 909]
    colors = ['#059669', '#10b981', '#34d399', '#6ee7b7', '#fbbf24', '#ef4444']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Champions", "9.8%", "32% выручки")
        st.metric("At Risk", "9.8%", "15% выручки")
    with col2:
        st.metric("Lost", "40%", "19% выручки")
        st.metric("Retention", "~20%", "6 месяцев")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(segments, counts, color=colors)
    ax.set_xlabel('Клиентов')
    ax.set_title('RFM Сегментация', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    for bar, val in zip(bars, counts):
        ax.text(val + 10, bar.get_y() + bar.get_height()/2, f'{val}', va='center')
    st.pyplot(fig)
    
    st.markdown("**Решение:** VIP-программа для Champions, реактивация At Risk/Lost.")

elif project == "🗄️ SQL-аналитика":
    st.header("🗄️ SQL-аналитика")
    st.markdown("**Вопрос:** Можно ли сделать RFM, когорты и воронку на чистом SQL?")
    
    st.subheader("📊 Ключевые SQL-концепции")
    sql_concepts = [
        ("CTE (WITH)", "Временные таблицы для читаемости"),
        ("NTILE(5)", "RFM-сегментация по квинтилям"),
        ("LAG() / LEAD()", "Динамика месяц-к-месяцу"),
        ("ROWS BETWEEN", "Скользящее среднее"),
        ("RANK / DENSE_RANK", "Ранжирование внутри стран"),
    ]
    for concept, desc in sql_concepts:
        st.write(f"**{concept}** — {desc}")
    
    st.subheader("📈 Результаты")
    months = ['2010-12', '2011-01', '2011-02', '2011-03', '2011-04', '2011-05']
    revenue = [572.7, 569.4, 447.1, 595.5, 469.2, 660.4]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(months, revenue, marker='o', color='#059669', linewidth=2, markersize=8)
    ax.fill_between(months, revenue, alpha=0.2, color='#059669')
    ax.set_ylabel('Выручка (тыс. $)')
    ax.set_title('Динамика выручки (SQL)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    st.metric("Champions", "25.9%", "RFM-сегмент")
    st.metric("Lost", "25.4%", "win-back потенциал")

elif project == "⚡ ETL-пайплайн":
    st.header("⚡ ETL-пайплайн")
    st.markdown("**Вопрос:** Можно ли автоматизировать весь путь от CSV до отчёта?")
    
    st.code("""
# Pipeline: CSV → SQLite → Витрина → PDF
python pipeline.py --input data.csv --output-dir reports/

Результат:
  ✅ База данных (3NF)
  ✅ SQL-витрина
  ✅ PNG-дашборд
  ✅ PDF-отчёт
    """, language="bash")
    
    st.subheader("🏗️ Архитектура")
    st.write("CSV → Staging → Normalization → Data Mart → Visualization → PDF")
    
    features = [
        "Автоопределение схемы (Retail / Generic)",
        "Batch-загрузка (5000 строк/бATCH)",
        "Валидация + нормализация",
        "SQL-витрина для аналитики",
        "Одна команда = полный отчёт"
    ]
    for f in features:
        st.write(f"✅ {f}")

elif project == "🔥 Продвинутый SQL":
    st.header("🔥 Продвинутый SQL")
    st.markdown("**Вопрос:** Что покажут продвинутые оконные функции?")
    
    st.subheader("📊 8 продвинутых запросов")
    queries = [
        "NTILE(4) — квартильная сегментация",
        "LAG + LEAD — динамика заказов клиента",
        "ROWS BETWEEN — кумулятивная выручка + MA",
        "RANK vs DENSE_RANK vs ROW_NUMBER",
        "CUME_DIST + PERCENT_RANK — процентили",
        "FIRST_VALUE / LAST_VALUE — границы окна",
        "Матрица R × F — комбинированная сегментация",
        "MoM + YoY — много-периодный рост"
    ]
    for i, q in enumerate(queries, 1):
        st.write(f"{i}. **{q}**")
    
    st.subheader("🎯 Ключевой инсайт")
    col1, col2 = st.columns(2)
    col1.metric("R4F4", "🔥 VIP", "свежие + частые")
    col2.metric("R1F1", "💤 Sleeping", "давно + редкие")
    
    # Визуализация матрицы
    r_labels = ['R1', 'R2', 'R3', 'R4']
    f_labels = ['F1', 'F2', 'F3', 'F4']
    matrix = [
        [200, 150, 100, 50],   # R1
        [180, 220, 160, 80],   # R2
        [120, 200, 280, 150],  # R3
        [50, 100, 200, 400]    # R4
    ]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(matrix, cmap='YlGn', aspect='auto')
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(f_labels)
    ax.set_yticklabels(r_labels)
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Recency')
    ax.set_title('Recency × Frequency Matrix', fontsize=14, fontweight='bold')
    
    for i in range(4):
        for j in range(4):
            text = ax.text(j, i, matrix[i][j], ha="center", va="center", color="black", fontweight='bold')
    
    plt.colorbar(im, ax=ax, label='Клиентов')
    st.pyplot(fig)

# Футер
st.sidebar.markdown("---")
st.sidebar.info("📊 Data Analyst Portfolio\n\n7 проектов\n20+ SQL-запросов\n144K строк данных")
