#!/usr/bin/env python3
"""
Проект 5: SQL-аналитика на SQLite.
10+ запросов: RFM, когорты, оконные функции, воронка.
"""

import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / 'retail_analytics.db'
OUTPUT_DIR = Path(__file__).parent

def run_query(conn, name, sql):
    """Выполняем запрос и выводим результат."""
    print(f"\n{'='*60}")
    print(f"📊 {name}")
    print(f"{'='*60}")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    return df

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    
    print("🗄️  Проект 5: SQL-аналитика на SQLite")
    print(f"📁 База: {DB_PATH}")
    
    # --- ЗАПРОС 1: Топ-10 клиентов по выручке ---
    # ЗАЧЕМ: Находим самых ценных клиентов — кто приносит больше денег
    # КАК: JOIN связывает customers с countries (чтобы показать страну)
    #      Сортируем по total_spent (общая сумма покупок) по убыванию
    #      LIMIT 10 — только топ-10
    q1 = """
    SELECT 
        c.customer_id,           -- ID клиента
        co.country_name,         -- Название страны (берём из справочника)
        c.total_orders,          -- Сколько заказов сделал
        ROUND(c.total_spent, 2) as total_revenue,  -- Общая выручка от клиента
        ROUND(c.total_spent / c.total_orders, 2) as avg_order_value  -- Средний чек
    FROM customers c             -- Таблица клиентов (основная)
    JOIN countries co ON c.country_id = co.country_id  -- Соединяем со странами
    WHERE c.total_orders > 0   -- Только те, кто реально покупал
    ORDER BY c.total_spent DESC  -- По убыванию выручки (сверху самые крупные)
    LIMIT 10                     -- Только 10 лучших
    """
    run_query(conn, "1. Топ-10 клиентов по выручке", q1)
    
    # --- ЗАПРОС 2: Выручка по странам (TOP-10) ---
    # ЗАЧЕМ: Узнаем, из каких стран больше всего денег
    # КАК: JOIN 4 таблиц: countries → customers → orders → order_items
    #      GROUP BY группирует по странам
    #      SUM(line_total) суммирует выручку
    #      COUNT(DISTINCT) считает уникальных клиентов и заказы
    q2 = """
    SELECT 
        co.country_name,                    -- Страна
        COUNT(DISTINCT c.customer_id) as customers,   -- Сколько уникальных клиентов
        COUNT(DISTINCT o.invoice_no) as orders,       -- Сколько заказов
        ROUND(SUM(oi.line_total), 2) as revenue       -- Общая выручка
    FROM countries co                       -- Начинаем со справочника стран
    JOIN customers c ON co.country_id = c.country_id   -- Клиенты этой страны
    JOIN orders o ON c.customer_id = o.customer_id     -- Их заказы
    JOIN order_items oi ON o.invoice_no = oi.invoice_no  -- Строки заказов
    GROUP BY co.country_name                -- Группировка по странам
    ORDER BY revenue DESC                   -- По убыванию выручки
    LIMIT 10                                -- Топ-10 стран
    """
    run_query(conn, "2. Топ-10 стран по выручке", q2)
    
    # --- ЗАПРОС 3: Динамика выручки по месяцам ---
    # ЗАЧЕМ: Смотрим, растёт или падает бизнес по месяцам
    # КАК: strftime('%Y-%m', date) — вытаскиваем год-месяц из даты
    #      COUNT(DISTINCT) — считаем уникальные заказы и клиентов
    #      SUM(line_total) — выручка за месяц
    #      AVG(line_total) — средний чек строки заказа
    q3 = """
    SELECT 
        strftime('%Y-%m', o.invoice_date) as month,        -- Месяц (2011-01)
        COUNT(DISTINCT o.invoice_no) as orders,             -- Заказов в месяц
        COUNT(DISTINCT o.customer_id) as unique_customers, -- Уникальных клиентов
        ROUND(SUM(oi.line_total), 2) as revenue,           -- Выручка
        ROUND(AVG(oi.line_total), 2) as avg_line_total      -- Средний чек строки
    FROM orders o                           -- Заказы
    JOIN order_items oi ON o.invoice_no = oi.invoice_no  -- Строки заказов
    GROUP BY month                          -- Группировка по месяцам
    ORDER BY month                          -- По хронологии
    """
    run_query(conn, "3. Динамика по месяцам", q3)
    
    # --- ЗАПРОС 4: RFM через SQL (CTE + CASE) ---
    # ЗАЧЕМ: Сегментируем клиентов по ценности (Recency, Frequency, Monetary)
    # КАК: 
    #   CTE (WITH) — создаём временную таблицу rfm_base с базовыми метриками
    #   recency_days — сколько дней прошло с последней покупки (меньше = лучше)
    #   frequency — сколько заказов сделал (больше = лучше)
    #   monetary — сколько потратил (больше = лучше)
    #   NTILE(5) — делим клиентов на 5 равных групп (квинтили)
    #   R_score — recency (5 = самые свежие, 1 = давно не покупали)
    #   F_score — frequency (5 = самые частые, 1 = редкие)
    #   M_score — monetary (5 = самые платёжеспособные, 1 = мало тратят)
    #   CASE — на основе скоров присваиваем сегмент
    q4 = """
    WITH rfm_base AS (                      -- Временная таблица с базовыми метриками
        SELECT 
            c.customer_id,
            -- Recency: сколько дней с последней покупки (опорная дата 2011-12-01)
            julianday('2011-12-01') - julianday(MAX(o.invoice_date)) as recency_days,
            -- Frequency: количество уникальных заказов
            COUNT(DISTINCT o.invoice_no) as frequency,
            -- Monetary: общая сумма покупок
            ROUND(SUM(oi.line_total), 2) as monetary
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.invoice_no = oi.invoice_no
        GROUP BY c.customer_id              -- Группировка по клиенту
    ),
    rfm_scores AS (                         -- Временная таблица со скорами
        SELECT 
            customer_id,
            recency_days,
            frequency,
            monetary,
            -- NTILE(5) делит на 5 равных групп. ORDER BY recency_days DESC:
            -- сверху самые свежие (малые recency_days), им присваивается 5
            NTILE(5) OVER (ORDER BY recency_days DESC) as R_score,
            -- frequency ASC: снизу редкие, сверху частые → частым присваивается 5
            NTILE(5) OVER (ORDER BY frequency ASC) as F_score,
            -- monetary ASC: снизу мало тратят, сверху много → крупным присваивается 5
            NTILE(5) OVER (ORDER BY monetary ASC) as M_score
        FROM rfm_base
    )
    SELECT 
        customer_id,
        ROUND(recency_days, 0) as recency,  -- Дни с последней покупки
        frequency,                          -- Частота заказов
        monetary,                           -- Денежная ценность
        R_score, F_score, M_score,          -- Скоры 1-5
        R_score + F_score + M_score as rfm_total,  -- Суммарный скор
        -- Сегментация по правилам:
        CASE 
            WHEN R_score >= 4 AND F_score >= 4 THEN 'Champions'      -- Лучшие из лучших
            WHEN R_score >= 3 AND F_score >= 3 AND M_score >= 3 THEN 'Loyal Customers'  -- Постоянные
            WHEN R_score >= 4 AND F_score <= 2 THEN 'New Customers'   -- Новички
            WHEN R_score <= 2 AND F_score >= 3 THEN 'At Risk'        -- Рискуют уйти
            WHEN R_score <= 2 AND F_score <= 2 THEN 'Lost'            -- Ушли
            ELSE 'Others'                      -- Все остальные
        END as segment
    FROM rfm_scores
    ORDER BY rfm_total DESC                 -- Сверху самые ценные
    LIMIT 15                                -- Только 15 для показа
    """
    df_rfm = run_query(conn, "4. RFM-сегментация (NTILE + CASE)", q4)
    
    # --- ЗАПРОС 5: Распределение RFM-сегментов ---
    # ЗАЧЕМ: Сколько клиентов в каждом сегменте — для планирования маркетинга
    # КАК: Повторяем логику RFM, но агрегируем по сегментам
    #      SUM(COUNT(*)) OVER() — общее количество клиентов (оконная функция)
    #      pct_total — процент от общего числа
    q5 = """
    WITH rfm_base AS (                      -- Та же база, что и в запросе 4
        SELECT 
            c.customer_id,
            julianday('2011-12-01') - julianday(MAX(o.invoice_date)) as recency_days,
            COUNT(DISTINCT o.invoice_no) as frequency,
            ROUND(SUM(oi.line_total), 2) as monetary
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.invoice_no = oi.invoice_no
        GROUP BY c.customer_id
    ),
    rfm_scores AS (
        SELECT 
            customer_id,
            NTILE(5) OVER (ORDER BY recency_days DESC) as R_score,
            NTILE(5) OVER (ORDER BY frequency ASC) as F_score,
            NTILE(5) OVER (ORDER BY monetary ASC) as M_score
        FROM rfm_base
    ),
    segments AS (
        SELECT 
            customer_id,
            CASE 
                WHEN R_score >= 4 AND F_score >= 4 THEN 'Champions'
                WHEN R_score >= 3 AND F_score >= 3 AND M_score >= 3 THEN 'Loyal Customers'
                WHEN R_score >= 4 AND F_score <= 2 THEN 'New Customers'
                WHEN R_score <= 2 AND F_score >= 3 THEN 'At Risk'
                WHEN R_score <= 2 AND F_score <= 2 THEN 'Lost'
                ELSE 'Others'
            END as segment
        FROM rfm_scores
    )
    SELECT 
        segment,                            -- Название сегмента
        COUNT(*) as customers,              -- Сколько клиентов
        -- SUM(COUNT(*)) OVER() — общее число клиентов (оконная функция без PARTITION)
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as pct_total  -- Процент
    FROM segments
    GROUP BY segment                        -- Группировка по сегментам
    ORDER BY customers DESC                 -- По убыванию
    """
    run_query(conn, "5. Распределение RFM-сегментов", q5)
    
    # --- ЗАПРОС 6: Когортный анализ (первый месяц покупки) ---
    # ЗАЧЕМ: Узнаем, сколько клиентов из каждой когорты (месяца привлечения) 
    #        возвращаются в последующие месяцы — retention
    # КАК:
    #   first_purchase CTE: для каждого клиента находим первый месяц покупки (когорта)
    #   activity CTE: для каждого заказа считаем, сколько месяцев прошло с когорты
    #   strftime('%Y', date) - strftime('%Y', date) — разница в годах × 12
    #   MAX(COUNT(...)) OVER (PARTITION BY cohort_month) — размер когорты
    #   retention_pct — процент оставшихся от исходного размера когорты
    q6 = """
    WITH first_purchase AS (                -- Первый месяц покупки для каждого клиента
        SELECT 
            customer_id,
            MIN(strftime('%Y-%m', invoice_date)) as cohort_month
        FROM orders
        GROUP BY customer_id              -- Группировка по клиенту
    ),
    activity AS (                           -- Активность по месяцам
        SELECT 
            o.customer_id,
            fp.cohort_month,                 -- Месяц привлечения
            strftime('%Y-%m', o.invoice_date) as activity_month,  -- Месяц активности
            -- Считаем разницу в месяцах между активностью и когортой:
            (strftime('%Y', o.invoice_date) - strftime('%Y', fp.cohort_month || '-01')) * 12 +
            (strftime('%m', o.invoice_date) - strftime('%m', fp.cohort_month || '-01')) as period_months
        FROM orders o
        JOIN first_purchase fp ON o.customer_id = fp.customer_id
    )
    SELECT 
        cohort_month,                        -- Месяц привлечения
        period_months,                       -- Сколько месяцев прошло (0 = первый)
        COUNT(DISTINCT customer_id) as active_customers,  -- Сколько клиентов активны
        -- MAX(...) OVER (PARTITION BY cohort_month) — находим размер когорты (period=0)
        -- Это оконная функция: максимум внутри каждой когорты
        ROUND(COUNT(DISTINCT customer_id) * 100.0 / 
            MAX(COUNT(DISTINCT customer_id)) OVER (PARTITION BY cohort_month), 1) as retention_pct
    FROM activity
    GROUP BY cohort_month, period_months     -- Группировка по когорте и периоду
    ORDER BY cohort_month, period_months     -- Сначала по когорте, потом по времени
    LIMIT 20                                -- Только 20 строк для компактности
    """
    run_query(conn, "6. Когортный анализ (retention)", q6)
    
    # --- ЗАПРОС 7: Скользящее среднее выручки (оконные функции) ---
    # ЗАЧЕМ: Сглаживаем колебания выручки, чтобы увидеть тренд
    # КАК:
    #   Внутренний подзапрос: считаем выручку по месяцам
    #   AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)
    #     — берём текущий месяц + 2 предыдущих, считаем среднее
    #   Это оконная функция с фреймом (frame specification)
    q7 = """
    SELECT 
        month,                               -- Месяц
        revenue,                             -- Выручка
        -- Скользящее среднее 3-месячное:
        -- ROWS BETWEEN 2 PRECEDING AND CURRENT ROW = текущая строка + 2 предыдущие
        ROUND(AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) as ma_3m
    FROM (
        -- Подзапрос: выручка по месяцам
        SELECT 
            strftime('%Y-%m', o.invoice_date) as month,
            ROUND(SUM(oi.line_total), 2) as revenue
        FROM orders o
        JOIN order_items oi ON o.invoice_no = oi.invoice_no
        GROUP BY month
    )
    ORDER BY month
    """
    run_query(conn, "7. Скользящее среднее (3-месячное)", q7)
    
    # --- ЗАПРОС 8: Ранг клиентов по выручке внутри страны ---
    # ЗАЧЕМ: Кто самый крупный клиент в каждой стране — для локальных менеджеров
    # КАК:
    #   PARTITION BY co.country_name — оконная функция работает внутри каждой страны отдельно
    #   RANK() — если у двоих одинаковая выручка, получают одинаковый ранг (с пропуском)
    #   DENSE_RANK() — тоже самое, но без пропуска (1, 2, 2, 3...)
    #   ROW_NUMBER() — просто номер строки (уникальный, даже при равенстве)
    q8 = """
    SELECT 
        co.country_name,                    -- Страна
        c.customer_id,                      -- Клиент
        ROUND(c.total_spent, 2) as revenue, -- Выручка
        -- Ранг с пропусками (1, 2, 2, 4... если третий = четвёртому)
        RANK() OVER (PARTITION BY co.country_name ORDER BY c.total_spent DESC) as country_rank,
        -- Плотный ранг (1, 2, 2, 3... без пропуска)
        DENSE_RANK() OVER (PARTITION BY co.country_name ORDER BY c.total_spent DESC) as dense_rank,
        -- Просто номер строки (всегда уникальный)
        ROW_NUMBER() OVER (PARTITION BY co.country_name ORDER BY c.total_spent DESC) as row_num
    FROM customers c
    JOIN countries co ON c.country_id = co.country_id
    WHERE c.total_orders > 0              -- Только активные клиенты
    ORDER BY co.country_name, country_rank  -- Сначала по стране, потом по рангу
    LIMIT 20                                -- Топ-20 для компактности
    """
    run_query(conn, "8. Ранг клиентов по странам (RANK/DENSE_RANK/ROW_NUMBER)", q8)
    
    # --- ЗАПРОС 9: Рост/падение выручки месяц к месяцу (LAG) ---
    # ЗАЧЕМ: Видим динамику: выросли или упали по сравнению с прошлым месяцем
    # КАК:
    #   LAG(revenue) OVER (ORDER BY month) — значение выручки из ПРЕДЫДУЩЕЙ строки
    #   diff = текущий - предыдущий (абсолютная разница)
    #   pct_change = diff / предыдущий × 100 (процент)
    #   LAG(..., 1, NULL) — смещение на 1 строку назад, NULL если нет предыдущей
    q9 = """
    WITH monthly AS (                       -- Выручка по месяцам
        SELECT 
            strftime('%Y-%m', o.invoice_date) as month,
            ROUND(SUM(oi.line_total), 2) as revenue
        FROM orders o
        JOIN order_items oi ON o.invoice_no = oi.invoice_no
        GROUP BY month
    )
    SELECT 
        month,                               -- Месяц
        revenue,                             -- Текущая выручка
        -- LAG — берём значение из предыдущей строки (прошлый месяц)
        LAG(revenue) OVER (ORDER BY month) as prev_revenue,
        -- Разница с прошлым месяцем
        ROUND(revenue - LAG(revenue) OVER (ORDER BY month), 2) as diff,
        -- Процентное изменение (может быть NULL для первого месяца)
        ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) * 100.0 / LAG(revenue) OVER (ORDER BY month), 1) as pct_change
    FROM monthly
    ORDER BY month
    """
    run_query(conn, "9. Рост/падение выручки (LAG)", q9)
    
    # --- ЗАПРОС 10: Топ-5 продуктов по выручке с долей от общей ---
    # ЗАЧЕМ: Какие товары приносят больше всего денег
    # КАК:
    #   SUM(oi.line_total) OVER() — оконная функция без PARTITION = сумма по ВСЕМ строкам
    #   pct_total = revenue / total_revenue × 100
    q10 = """
    SELECT 
        p.stock_code,                       -- Код товара
        p.description,                      -- Название
        SUM(oi.quantity) as total_qty,      -- Продано штук
        ROUND(SUM(oi.line_total), 2) as revenue,  -- Выручка
        -- Доля от общей выручки: оконная функция SUM() OVER() считает общую сумму
        ROUND(SUM(oi.line_total) * 100.0 / SUM(SUM(oi.line_total)) OVER(), 2) as pct_total
    FROM products p
    JOIN order_items oi ON p.stock_code = oi.stock_code
    GROUP BY p.stock_code                  -- Группировка по товару
    ORDER BY revenue DESC                  -- По убыванию выручки
    LIMIT 5                                 -- Топ-5
    """
    run_query(conn, "10. Топ-5 продуктов (доля от выручки)", q10)
    
    # --- ЗАПРОС 11: Повторные покупки (интервал между заказами) ---
    # ЗАЧЕМ: Насколько часто клиенты возвращаются — для планирования CRM
    # КАК:
    #   LAG(invoice_date) OVER (PARTITION BY customer_id ORDER BY invoice_date)
    #     — предыдущий заказ КОНКРЕТНОГО клиента
    #   julianday() - julianday() — разница в днях (SQLite-функция)
    #   AVG(...) — средний интервал для клиентов с 2+ заказами
    q11 = """
    WITH order_dates AS (                   -- Все заказы с предыдущей датой
        SELECT 
            customer_id,
            invoice_date,
            -- LAG с PARTITION: берём предыдущий заказ ТОГО ЖЕ клиента
            LAG(invoice_date) OVER (PARTITION BY customer_id ORDER BY invoice_date) as prev_order
        FROM orders
    )
    SELECT 
        customer_id,                         -- Клиент
        COUNT(*) as orders,                  -- Всего заказов
        -- Средний интервал между заказами (только где prev_order есть)
        ROUND(AVG(julianday(invoice_date) - julianday(prev_order)), 1) as avg_days_between,
        MIN(julianday(invoice_date) - julianday(prev_order)) as min_gap,   -- Минимум
        MAX(julianday(invoice_date) - julianday(prev_order)) as max_gap    -- Максимум
    FROM order_dates
    WHERE prev_order IS NOT NULL             -- Только повторные заказы
    GROUP BY customer_id                    -- Группировка по клиенту
    HAVING COUNT(*) >= 2                    -- Только с 2+ заказами
    ORDER BY avg_days_between               -- Сверху самые частые
    LIMIT 15                                -- Топ-15
    """
    run_query(conn, "11. Интервал между повторными покупками (LAG)", q11)
    
    # --- ЗАПРОС 12: Воронка по месяцам (уникальные пользователи) ---
    # ЗАЧЕМ: Сколько новых и вернувшихся клиентов каждый месяц + ARPU
    # КАК:
    #   COUNT(DISTINCT customer_id) — уникальные клиенты (новые + вернувшиеся)
    #   revenue / unique_customers = ARPU (Average Revenue Per User)
    #   Это proxy-метрика retention — если клиентов растёт, значит удерживаем
    q12 = """
    SELECT 
        strftime('%Y-%m', o.invoice_date) as month,       -- Месяц
        COUNT(DISTINCT o.customer_id) as unique_customers,  -- Уникальных клиентов
        COUNT(DISTINCT o.invoice_no) as orders,            -- Заказов
        ROUND(SUM(oi.line_total), 2) as revenue,          -- Выручка
        -- ARPU: сколько денег в среднем принёс один клиент
        ROUND(SUM(oi.line_total) / COUNT(DISTINCT o.customer_id), 2) as arpu
    FROM orders o
    JOIN order_items oi ON o.invoice_no = oi.invoice_no
    GROUP BY month                          -- По месяцам
    ORDER BY month                          -- По хронологии
    """
    run_query(conn, "12. Воронка по месяцам (ARPU, retention proxy)", q12)
    
    conn.close()
    
    print("\n" + "="*60)
    print("🎉 Все 12 SQL-запросов выполнены!")
    print("="*60)

if __name__ == "__main__":
    main()
