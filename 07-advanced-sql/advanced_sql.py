#!/usr/bin/env python3
"""
Проект 7: Продвинутые оконные функции на чистом SQL.
Демонстрация: NTILE, LAG/LEAD, ROWS BETWEEN, RANK, CUME_DIST.
"""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / '05-sql-analytics' / 'retail_analytics.db'

def run_query(conn, name, sql):
    print(f"\n{'='*60}")
    print(f"📊 {name}")
    print(f"{'='*60}")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    return df

def main():
    conn = sqlite3.connect(DB_PATH)
    
    print("🚀 Проект 7: Продвинутые оконные функции")
    print(f"📁 База: {DB_PATH}")
    
    # --- ЗАПРОС 1: Квартильное распределение выручки (NTILE) ---
    # ЗАЧЕМ: Делим клиентов на 4 равные группы по выручке для сегментации
    # КАК: NTILE(4) делит на 4 квартиля. Квартиль 1 = топ-25% по выручке.
    q1 = """
    SELECT 
        customer_id,
        ROUND(total_spent, 2) as revenue,
        total_orders as orders,
        -- NTILE(4) — делим на 4 равные группы по убыванию выручки
        -- Квартиль 1 = самые крупные (топ-25%), 4 = самые мелкие
        NTILE(4) OVER (ORDER BY total_spent DESC) as revenue_quartile,
        -- ROW_NUMBER — просто номер по убыванию выручки
        ROW_NUMBER() OVER (ORDER BY total_spent DESC) as revenue_rank
    FROM customers
    WHERE total_orders > 0
    ORDER BY revenue DESC
    LIMIT 12
    """
    run_query(conn, "1. Квартильное распределение (NTILE)", q1)
    
    # --- ЗАПРОС 2: Динамика покупок клиента (LAG + LEAD) ---
    # ЗАЧЕМ: Для каждого клиента смотрим, что было до и после конкретного заказа
    # КАК: LAG — предыдущий заказ, LEAD — следующий заказ
    #      PARTITION BY customer_id — окно внутри одного клиента
    #      ORDER BY invoice_date — по хронологии
    q2 = """
    SELECT 
        customer_id,
        invoice_date,
        invoice_no,
        -- LAG: предыдущий заказ этого клиента (смещение на 1 назад)
        LAG(invoice_date) OVER (PARTITION BY customer_id ORDER BY invoice_date) as prev_order,
        -- LEAD: следующий заказ этого клиента (смещение на 1 вперёд)
        LEAD(invoice_date) OVER (PARTITION BY customer_id ORDER BY invoice_date) as next_order,
        -- Разница с предыдущим заказом в днях
        julianday(invoice_date) - julianday(
            LAG(invoice_date) OVER (PARTITION BY customer_id ORDER BY invoice_date)
        ) as days_since_prev
    FROM orders
    WHERE customer_id IN (12346, 12748, 14911)  -- Только 3 клиента для наглядности
    ORDER BY customer_id, invoice_date
    LIMIT 15
    """
    run_query(conn, "2. Динамика заказов клиента (LAG + LEAD)", q2)
    
    # --- ЗАПРОС 3: Скользящие метрики (ROWS BETWEEN) ---
    # ЗАЧЕМ: Сглаживаем колебания, считаем кумулятивные суммы
    # КАК: ROWS BETWEEN UNBOUNDED PRECEDING — от начала до текущей строки
    #      ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING — текущая + 1 до и 1 после
    q3 = """
    WITH monthly AS (
        SELECT 
            strftime('%Y-%m', o.invoice_date) as month,
            ROUND(SUM(oi.line_total), 2) as revenue,
            COUNT(DISTINCT o.invoice_no) as orders
        FROM orders o
        JOIN order_items oi ON o.invoice_no = oi.invoice_no
        GROUP BY month
        ORDER BY month
    )
    SELECT 
        month,
        revenue,
        orders,
        -- Кумулятивная сумма: от начала до текущего месяца
        ROUND(SUM(revenue) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) as cumulative_revenue,
        -- Скользящее среднее 3-месячное
        ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) as ma_3m,
        -- Скользящее среднее по центру (предыдущий + текущий + следующий)
        ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING), 2) as ma_center
    FROM monthly
    ORDER BY month
    """
    run_query(conn, "3. Скользящие метрики (ROWS BETWEEN)", q3)
    
    # --- ЗАПРОС 4: Разница между ранжированиями ---
    # ЗАЧЕМ: Показываем разницу между RANK, DENSE_RANK, ROW_NUMBER на одних данных
    # КАК: Все три функции с одинаковым PARTITION и ORDER BY
    #      Создаём искусственные совпадения (ROUND total_spent до сотен)
    q4 = """
    SELECT 
        customer_id,
        ROUND(total_spent, -2) as revenue_bucket,  -- Округляем до сотен для совпадений
        total_orders,
        -- RANK: пропускает номера при совпадениях (1, 2, 2, 4...)
        RANK() OVER (ORDER BY ROUND(total_spent, -2) DESC) as rnk,
        -- DENSE_RANK: не пропускает (1, 2, 2, 3...)
        DENSE_RANK() OVER (ORDER BY ROUND(total_spent, -2) DESC) as dense_rnk,
        -- ROW_NUMBER: всегда уникальный (1, 2, 3, 4...)
        ROW_NUMBER() OVER (ORDER BY ROUND(total_spent, -2) DESC, customer_id) as row_num
    FROM customers
    WHERE total_orders > 0
    ORDER BY revenue_bucket DESC, customer_id
    LIMIT 15
    """
    run_query(conn, "4. Сравнение RANK / DENSE_RANK / ROW_NUMBER", q4)
    
    # --- ЗАПРОС 5: Процентильное ранжирование (CUME_DIST + PERCENT_RANK) ---
    # ЗАЧЕМ: Узнаём, в каком процентиле находится клиент по выручке
    # КАК: CUME_DIST — доля строк со значением <= текущему (0..1)
    #      PERCENT_RANK — (ранг - 1) / (всего - 1) (0..1)
    q5 = """
    SELECT 
        customer_id,
        ROUND(total_spent, 2) as revenue,
        total_orders,
        -- CUME_DIST: какая доля клиентов зарабатывает <= этого клиента
        -- Например, 0.95 = 95% клиентов зарабатывают меньше или столько же
        ROUND(CUME_DIST() OVER (ORDER BY total_spent), 3) as cum_dist,
        -- PERCENT_RANK: ранг в процентах (0 = минимум, 1 = максимум)
        ROUND(PERCENT_RANK() OVER (ORDER BY total_spent), 3) as pct_rank,
        -- ROW_NUMBER для наглядности
        ROW_NUMBER() OVER (ORDER BY total_spent) as position
    FROM customers
    WHERE total_orders > 0
    ORDER BY revenue DESC
    LIMIT 12
    """
    run_query(conn, "5. Процентильное ранжирование (CUME_DIST + PERCENT_RANK)", q5)
    
    # --- ЗАПРОС 6: FIRST_VALUE / LAST_VALUE (границы окна) ---
    # ЗАЧЕМ: Находим первого и последнего клиента в сегменте
    # КАК: FIRST_VALUE — первое значение в окне
    #      LAST_VALUE — последнее значение в окне (нужен правильный фрейм!)
    #      RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING — всё окно
    q6 = """
    SELECT DISTINCT
        co.country_name,
        c.customer_id,
        ROUND(c.total_spent, 2) as revenue,
        -- FIRST_VALUE: ID клиента с максимальной выручкой В ЭТОЙ СТРАНЕ
        FIRST_VALUE(c.customer_id) OVER (
            PARTITION BY co.country_name 
            ORDER BY c.total_spent DESC 
            RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as top_customer_in_country,
        -- LAST_VALUE: ID клиента с минимальной выручкой В ЭТОЙ СТРАНЕ
        LAST_VALUE(c.customer_id) OVER (
            PARTITION BY co.country_name 
            ORDER BY c.total_spent DESC 
            RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) as bottom_customer_in_country
    FROM customers c
    JOIN countries co ON c.country_id = co.country_id
    WHERE c.total_orders > 0
    ORDER BY co.country_name, revenue DESC
    LIMIT 12
    """
    run_query(conn, "6. FIRST_VALUE / LAST_VALUE внутри страны", q6)
    
    # --- ЗАПРОС 7: Сегментация по квартилям Recency + Frequency ---
    # ЗАЧЕМ: Комбинированная сегментация: свежесть × частота
    # КАК: Два NTILE — один по recency, другой по frequency
    #      Перекрёстная таблица (matrix) сегментации
    q7 = """
    WITH customer_metrics AS (
        SELECT 
            c.customer_id,
            -- Recency: дни с последней покупки
            julianday('2011-12-01') - julianday(MAX(o.invoice_date)) as recency_days,
            -- Frequency: количество заказов
            COUNT(DISTINCT o.invoice_no) as freq,
            -- Monetary
            ROUND(SUM(oi.line_total), 2) as monetary
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.invoice_no = oi.invoice_no
        GROUP BY c.customer_id
    )
    SELECT 
        customer_id,
        ROUND(recency_days, 0) as recency,
        freq,
        monetary,
        -- Recency квартиль: 1 = давно, 4 = свежие
        NTILE(4) OVER (ORDER BY recency_days DESC) as R_quartile,
        -- Frequency квартиль: 1 = редкие, 4 = частые
        NTILE(4) OVER (ORDER BY freq ASC) as F_quartile,
        -- Сегмент: комбинация R + F
        'R' || NTILE(4) OVER (ORDER BY recency_days DESC) || 
        'F' || NTILE(4) OVER (ORDER BY freq ASC) as segment_code,
        CASE 
            WHEN NTILE(4) OVER (ORDER BY recency_days DESC) >= 3 
                 AND NTILE(4) OVER (ORDER BY freq ASC) >= 3 THEN '🔥 VIP'
            WHEN NTILE(4) OVER (ORDER BY recency_days DESC) >= 3 
                 AND NTILE(4) OVER (ORDER BY freq ASC) <= 2 THEN '✨ New'
            WHEN NTILE(4) OVER (ORDER BY recency_days DESC) <= 2 
                 AND NTILE(4) OVER (ORDER BY freq ASC) >= 3 THEN '⚠️ At Risk'
            WHEN NTILE(4) OVER (ORDER BY recency_days DESC) <= 2 
                 AND NTILE(4) OVER (ORDER BY freq ASC) <= 2 THEN '💤 Sleeping'
            ELSE '😐 Regular'
        END as segment_name
    FROM customer_metrics
    ORDER BY monetary DESC
    LIMIT 12
    """
    run_query(conn, "7. Матрица Recency × Frequency (NTILE + CASE)", q7)
    
    # --- ЗАПРОС 8: Дельта с предыдущим и рост в процентах (LAG) ---
    # ЗАЧЕМ: Видим абсолютный и процентный рост по месяцам
    # КАК: LAG(revenue, 1) — предыдущая строка
    #      LAG(revenue, 2) — строка на 2 назад (для сравнения год к году)
    q8 = """
    WITH monthly AS (
        SELECT 
            strftime('%Y-%m', o.invoice_date) as month,
            ROUND(SUM(oi.line_total), 2) as revenue,
            COUNT(DISTINCT o.invoice_no) as orders
        FROM orders o
        JOIN order_items oi ON o.invoice_no = oi.invoice_no
        GROUP BY month
    )
    SELECT 
        month,
        revenue,
        -- Предыдущий месяц
        LAG(revenue, 1) OVER (ORDER BY month) as prev_month,
        -- Разница с предыдущим
        ROUND(revenue - LAG(revenue, 1) OVER (ORDER BY month), 2) as mom_change,
        -- MoM % (month-over-month)
        ROUND((revenue - LAG(revenue, 1) OVER (ORDER BY month)) * 100.0 / 
            LAG(revenue, 1) OVER (ORDER BY month), 1) as mom_pct,
        -- Тот же месяц год назад (если есть)
        LAG(revenue, 12) OVER (ORDER BY month) as yoy_prev,
        -- YoY % (year-over-year)
        ROUND((revenue - LAG(revenue, 12) OVER (ORDER BY month)) * 100.0 / 
            LAG(revenue, 12) OVER (ORDER BY month), 1) as yoy_pct
    FROM monthly
    ORDER BY month
    """
    run_query(conn, "8. MoM + YoY рост (LAG с разными смещениями)", q8)
    
    conn.close()
    
    print("\n" + "="*60)
    print("🎉 Проект 7 завершён: 8 продвинутых запросов")
    print("="*60)
    print("\n📚 Изучено:")
    print("  • NTILE(4) — квартильное распределение")
    print("  • LAG/LEAD — смещение внутри PARTITION")
    print("  • ROWS BETWEEN — фреймы окон")
    print("  • RANK vs DENSE_RANK vs ROW_NUMBER")
    print("  • CUME_DIST / PERCENT_RANK — процентили")
    print("  • FIRST_VALUE / LAST_VALUE — границы окна")
    print("  • Комбинированная сегментация (матрица)")

if __name__ == "__main__":
    main()
