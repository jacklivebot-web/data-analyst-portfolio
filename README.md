# 📊 Портфолио Data Analyst

> **7 production-ready проектов с дашбордами, SQL-пайплайнами и автоматической отчётностью.**

---

## 🚀 Быстрый старт

```bash
git clone https://github.com/jacklivebot-web/data-analyst-portfolio.git
cd data-analyst-portfolio

# Установка зависимостей
uv venv && uv pip install pandas numpy matplotlib seaborn plotly

# Запуск любого проекта
python auto_report.py --input data.csv --type funnel --output-dir reports/
```

---

## 📈 Обзор проектов

| # | Проект | Стек | Статус |
|---|--------|------|--------|
| 1 | [Воронка e-commerce](#-проект-1-воронка-e-commerce) | Python, pandas, matplotlib | ✅ |
| 2 | [A/B-тестирование](#-проект-2-ab-тестирование) | Python, scipy, статистика | ✅ |
| 3 | [Прогноз оттока](#-проект-3-прогноз-оттока) | Python, scikit-learn | ✅ |
| 4 | [RFM-сегментация](#-проект-4-rfm-сегментация) | Python, pandas, RFM | ✅ |
| 5 | [SQL-аналитика](#-проект-5-sql-аналитика) | SQLite, CTE, оконные функции | ✅ |
| 6 | [ETL-пайплайн](#-проект-6-etl-пайплайн) | Python, SQLite, автоматизация | ✅ |
| 7 | [Продвинутый SQL](#-проект-7-продвинутый-sql) | SQLite, NTILE, LAG/LEAD | ✅ |

---

## 📌 Проект 1: Воронка e-commerce

**Вопрос:** Где теряются покупатели на пути к заказу?

![Дашборд воронки](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/01-ecommerce-funnel/dashboard_preview.png)

**Ключевые метрики:**
- Конверсия: 2.1% → потенциал 8.5%
- Главная потеря: 65% уходят после корзины
- Mobile vs Desktop: 9.2% vs 11.0%
- Лучший канал: Referral (11.5%)

**Решение:** Упростить mobile-checkout, проверить аудиторию paid social.

---

## 📌 Проект 2: A/B-тестирование

**Вопрос:** Вариант B статистически лучше A?

![Дашборд A/B](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/02-ab-test-analysis/dashboard_preview.png)

**Ключевые метрики:**
- Конверсия: 12.26% → 15.28% (+24.6%)
- p-value < 0.0001, доверие 99%
- ARPU: $10.40 → $13.31 (+28%)
- 95% CI: [14.3%, 16.3%] — пересечений нет

**Решение:** Раскатить вариант B на 100% трафика.

---

## 📌 Проект 3: Прогноз оттока

**Вопрос:** Кто уйдёт в следующем месяце? Как их удержать?

![Дашборд оттока](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/03-churn-prediction/dashboard_preview.png)

**Ключевые метрики:**
- Точность модели: 87.2% (ROC-AUC)
- Топ-20% по Risk Score: 53.5% отток
- Отток Free-плана: 37.8%
- Ключевые сигналы: >30 дней без покупки, снижение частоты

**Решение:** Триггерные кампании для high-risk сегмента.

---

## 📌 Проект 4: RFM-сегментация

**Вопрос:** Кто самые ценные клиенты?

*Реальные данные: 144 541 транзакция, 2 708 клиентов, 6 месяцев*

![Дашборд RFM](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/04-retail-rfm-analysis/dashboard_preview.png)

**Ключевые метрики:**
- Champions (9.8%) = 32% выручки
- At Risk (9.8%) = 15% выручки — нужна реактивация
- Lost (40%) = 19% выручки — win-back кампания
- Retention (6 мес): ~20%

**Решение:** VIP-программа для Champions, реактивация At Risk/Lost.

---

## 📌 Проект 5: SQL-аналитика

**Вопрос:** Можно ли сделать RFM, когорты и воронку на чистом SQL?

*144K строк → Нормализованная SQLite БД (3NF) → 12 аналитических запросов*

![Дашборд SQL](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/05-sql-analytics/dashboard_sql.png)

**Что сделано:**
- **ETL**: CSV → 5 нормализованных таблиц (countries, customers, products, orders, order_items)
- **RFM-сегментация** через `NTILE(5)` + `CASE`
- **Когортный анализ** с retention через оконные функции
- **Скользящее среднее** (`ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`)
- **MoM-рост** через `LAG()` для месяц-к-месяцу
- **Ранжирование** (`RANK`, `DENSE_RANK`, `ROW_NUMBER`) внутри стран

**Ключевой инсайт:** 25.9% Champions + 25.4% Lost = понятная матрица действий.

**Стек:** SQLite, CTE, оконные функции, JOIN, подзапросы

---

## 📌 Проект 6: ETL-пайплайн

**Вопрос:** Можно ли автоматизировать весь путь от CSV до отчёта?

**Пайплайн:**
```
CSV → SQLite (3NF) → SQL-витрина → PNG-дашборд → PDF-отчёт
```

**Возможности:**
- Автоопределение схемы (Retail / Generic)
- Batch-загрузка (5000 строк/бATCH для скорости)
- Валидация + нормализация
- Одна команда: `python pipeline.py --input data.csv`

**Стек:** Python, SQLite, reportlab, matplotlib

---

## 📌 Проект 7: Продвинутый SQL

**Вопрос:** Что покажут продвинутые оконные функции?

**8 продвинутых запросов:**
1. **NTILE(4)** — квартильная сегментация клиентов
2. **LAG + LEAD** — динамика заказов внутри клиента
3. **ROWS BETWEEN** — кумулятивная выручка + скользящее среднее
4. **RANK vs DENSE_RANK vs ROW_NUMBER** — сравнение ранжирований
5. **CUME_DIST + PERCENT_RANK** — процентильное позиционирование
6. **FIRST_VALUE / LAST_VALUE** — лучший/худший клиент в стране
7. **Матрица R × F** — комбинированная сегментация Recency-Frequency
8. **MoM + YoY** — много-периодный анализ роста

**Ключевой инсайт:** R4F4 = 🔥 VIP (свежие + частые). R1F1 = 💤 Спящие.

**Стек:** SQLite, продвинутые оконные функции

---

## 🛠️ Технологический стек

| Категория | Инструменты |
|-----------|-------------|
| **Данные** | SQL (SQLite, PostgreSQL), pandas, numpy |
| **Аналитика** | Статистика, A/B-тесты, RFM, когортный анализ, ML |
| **Визуализация** | matplotlib, seaborn, Plotly, HTML-дашборды |
| **Автоматизация** | Python-скрипты, ETL-пайплайны, генерация отчётов |
| **Инфраструктура** | Git, GitHub, uv, Jupyter, Linux |

---

## 📁 Структура репозитория

```
data-analyst-portfolio/
├── README.md                          ← Вы здесь
├── auto_report.py                     🤖 CSV → Дашборд + PDF (авто)
├── dashboards.py                        # Генератор интерактивных HTML
│
├── 01-ecommerce-funnel/
│   ├── dashboard.html                   🎯 Интерактивная воронка
│   ├── dashboard_preview.png            📊 Статичный превью
│   ├── 01_ecommerce_funnel.ipynb        📓 Jupyter ноутбук
│   └── analyze_funnel.py              🔧 Python-скрипт
│
├── 02-ab-test-analysis/
│   ├── dashboard.html                   🧪 Дашборд стат. значимости
│   ├── dashboard_preview.png            📊 Статичный превью
│   ├── 02_ab_test.ipynb               📓 Jupyter ноутбук
│   └── analyze_ab.py                  🔧 Python-скрипт
│
├── 03-churn-prediction/
│   ├── dashboard.html                   🔄 Risk Score + сегменты
│   ├── dashboard_preview.png            📊 Статичный превью
│   ├── 03_churn_prediction.ipynb      📓 Jupyter ноутбук
│   └── analyze_churn.py               🔧 Python-скрипт
│
├── 04-retail-rfm-analysis/
│   ├── dashboard.html                   🛍️ RFM + география + динамика
│   ├── dashboard_preview.png            📊 Статичный превью
│   ├── online_retail.csv              💾 Реальные данные (144K строк)
│   ├── 04_retail_rfm.ipynb            📓 Jupyter ноутбук
│   └── analyze_retail.py              🔧 Python-скрипт
│
├── 05-sql-analytics/
│   ├── etl.py                           🗄️ CSV → SQLite (3NF)
│   ├── sql_analytics.py               📊 12 SQL-запросов с комментариями
│   ├── retail_analytics.db            💾 База данных SQLite
│   └── dashboard_sql.png              📈 Визуализация SQL-результатов
│
├── 06-etl-pipeline/
│   ├── etl_pipeline.py                  🤖 Полный пайплайн CSV → PDF
│   └── pipeline.py                      ⚡ Модульная обёртка
│
└── 07-advanced-sql/
    ├── advanced_sql.py                  ⚡ 8 запросов с оконными функциями
    └── README.md                        # Документация
```

---

## 📄 PDF-отчёты

Два готовых презентационных PDF:

| Отчёт | Страниц | Назначение |
|-------|---------|------------|
| `Data_Analyst_Portfolio_Report.pdf` | 8 | Презентация портфолио со всеми дашбордами |
| `Executive_Summary_Report.pdf` | 7 | Бизнес-отчёт для руководства (метрики + ROI) |

---

## ⚡ Автоматизация

**Генератор автоотчётов:**
```bash
# Воронка e-commerce
python auto_report.py --input funnel.csv --type funnel --output-dir reports/

# A/B-тест
python auto_report.py --input ab_test.csv --type ab_test --output-dir reports/

# Прогноз оттока
python auto_report.py --input customers.csv --type churn --output-dir reports/

# RFM-сегментация
python auto_report.py --input retail.csv --type rfm --output-dir reports/
```

**Результат:** `dashboard_TYPE.png` + `dashboard_TYPE.html` + `auto_report_TYPE.pdf`

---

## 🎯 Бизнес-вопросы и ответы

1. **Где теряем клиентов?** → Воронка с разбивкой по устройствам/каналам
2. **Какой вариант лучше?** → Статистический A/B-тест с доверительными интервалами
3. **Кто уйдёт?** → ML-модель с 87% точностью + скоринг риска
4. **Кто приносит деньги?** → RFM-сегментация с выделением VIP
5. **Может ли SQL всё это?** → 20+ запросов, доказывающих аналитическую мощь SQL
6. **Можно ли автоматизировать?** → ETL-пайплайн в одну команду
7. **Что покажут оконные функции?** → Продвинутые матрицы сегментации

---

**Лицензия:** MIT  
**Обновлено:** 2026-06-01
