# 🧠 Data Analyst Portfolio: Human + AI

> **Данные → Анализ → Дашборды → Решения**
>
> 4 полноценных аналитических отчёта с интерактивными дашбордами.
> GitHub: `github.com/jacklivebot-web/data-analyst-portfolio`

---

## 📊 Быстрый доступ к отчётам

| # | Проект | Дашборд | Запрос | Статус |
|---|--------|---------|--------|--------|
| 1 | **E-commerce Funnel** | [`dashboard.html`](./01-ecommerce-funnel/dashboard.html) | Где теряются пользователи? | ✅ Готово |
| 2 | **A/B Test** | [`dashboard.html`](./02-ab-test-analysis/dashboard.html) | Какой вариант лучше? | ✅ Готово |
| 3 | **Churn Prediction** | [`dashboard.html`](./03-churn-prediction/dashboard.html) | Кто уйдёт? Как спасти? | ✅ Готово |
| 4 | **Retail RFM** | [`dashboard.html`](./04-retail-rfm-analysis/dashboard.html) | Кто самые ценные клиенты? | ✅ Готово |
| 5 | **SQL Analytics** | [`dashboard_sql.png`](./05-sql-analytics/dashboard_sql.png) | ETL + 12 SQL-запросов | ✅ Готово |
| 6 | **ETL Pipeline** | — | CSV → SQLite → PDF (авто) | ✅ Готово |
| 7 | **Advanced SQL** | — | Оконные функции + сегментация | ✅ Готово |

---

## 🎯 Бизнес-запросы и ответы

### 📌 Запрос 1: "Где в воронке теряются покупатели?"
**Проект:** [01-ecommerce-funnel](./01-ecommerce-funnel/)

![Funnel Dashboard](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/01-ecommerce-funnel/dashboard_preview.png)

| Метрика | Значение | Действие |
|---------|----------|----------|
| Воронка: View → Cart → Purchase | 100% → 40% → 25% | Улучшить checkout flow |
| Mobile vs Desktop конверсия | 9.2% vs 11.0% | Проверить UX мобильного оформления |
| Лучший канал | Referral (11.5%) | Масштабировать реферальную программу |
| Проблемный канал | Paid Social (9.2%, высокий трафик) | Проверить качество аудитории |

**Решение:** A/B тест упрощённого mobile-checkout + аудит paid social аудитории.

---

### 📌 Запрос 2: "Вариант B лучше A? Насколько значимо?"
**Проект:** [02-ab-test-analysis](./02-ab-test-analysis/)

![AB Test Dashboard](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/02-ab-test-analysis/dashboard_preview.png)

| Метрика | Variant A | Variant B | Разница | Значимость |
|---------|-----------|-----------|---------|------------|
| Конверсия | 12.26% | 15.28% | **+24.6%** | ✅ p < 0.0001 |
| 95% CI | [11.4%, 13.2%] | [14.3%, 16.3%] | — | Пересечения нет |
| ARPU | $10.40 | $13.31 | **+28.0%** | — |
| MDE | — | — | — | 1.29% (достаточно) |

**Решение:** Раскатить вариант B на 100% трафика. Ожидаемый прирост выручки: +28% на пользователя.

---

### 📌 Запрос 3: "Кто из клиентов уйдёт? Как их удержать?"
**Проект:** [03-churn-prediction](./03-churn-prediction/)

![Churn Dashboard](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/03-churn-prediction/dashboard_preview.png)

| Сегмент | Размер | Отток | Стратегия |
|---------|--------|-------|-----------|
| Все пользователи | 3,000 | 25.6% | Базовый уровень |
| Топ-20% по Risk Score | 600 | **53.5%** | 🔴 Триггерные кампании немедленно |
| План Free | 1,191 | 37.8% | 🟡 Улучшить onboarding + upsell |
| >14 дней без входа + <3 сессий | ~350 | ~50% | 🟠 Персональные предложения |

**Решение:** Автоматическая email-цепочка для топ-20% risk score. Для Free-плана — ограниченный триал Pro.

---

### 📌 Запрос 4: "Кто наши самые ценные клиенты? Где расти?"
**Проект:** [04-retail-rfm-analysis](./04-retail-rfm-analysis/) — **реальные данные**

![RFM Dashboard](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/04-retail-rfm-analysis/dashboard_preview.png)

| Сегмент | Клиенты | Выручка | Доля | Стратегия |
|---------|---------|---------|------|-----------|
| **Champions** | 267 (9.8%) | $222K | 32% | VIP-программа, ранний доступ |
| **Loyal** | 480 (17.6%) | $170K | 25% | Реферальные бонусы, upsell |
| **At Risk** | 267 (9.8%) | $105K | 15% | 🔴 Реактивация срочно |
| **Lost** | 1,094 (40%) | $128K | 19% | Win-back кампания |
| Retention (6 мес.) | — | ~20% | — | Улучшить onboarding |
| EU рынок | — | $52K | 7.5% | 🟢 Расширение в DE, FR, NL |

**Решение:** 1) Реактивация At Risk/Lost через email. 2) VIP-программа для Champions. 3) Тестировать EU рынок.

---

## 🚀 Как запустить

### ⚡ Быстрый старт — автоотчёт
Закинь CSV — получи PDF + дашборд. Автоматически:

```bash
# Воронка e-commerce
python auto_report.py --input data.csv --type funnel --output-dir reports/

# A/B тест
python auto_report.py --input data.csv --type ab_test --output-dir reports/

# Прогноз оттока
python auto_report.py --input data.csv --type churn --output-dir reports/

# RFM-сегментация
python auto_report.py --input data.csv --type rfm --output-dir reports/
```

**Результат:** `reports/dashboard_TYPE.png` + `.html` + `auto_report_TYPE_TIMESTAMP.pdf`

### 📊 Полный запуск
```bash
git clone https://github.com/jacklivebot-web/data-analyst-portfolio.git
cd data-analyst-portfolio
uv venv && uv pip install pandas numpy plotly matplotlib

# Автоотчёт (любые данные)
python auto_report.py --input your_data.csv --type funnel --output-dir reports/

# Или интерактивные дашборды
open 01-ecommerce-funnel/dashboard.html
open 02-ab-test-analysis/dashboard.html
open 03-churn-prediction/dashboard.html
open 04-retail-rfm-analysis/dashboard.html

# Jupyter Notebook
uv pip install jupyter
uv run jupyter lab
```

---

## 🧠 Методология: Human + AI

**Евгений** задаёт бизнес-вопрос → **Jack** (Hermes Agent) генерирует данные, SQL, Python, дашборды → **Евгений** валидирует и принимает решение.

**Результат:** ad-hoc аналитика в 6–10 раз быстрее классического подхода.

---

## 📁 Структура

```
data-analyst-portfolio/
├── README.md                          ← Вы здесь
├── HUMAN_AI_HOW_IT_WORKS.md           # Архитектура Human+AI
├── auto_report.py                     🤖 CSV → PDF + дашборд (автоматика)
├── dashboards.py                        # Генератор интерактивных HTML
│
├── 01-ecommerce-funnel/
│   ├── dashboard.html                   🎯 Воронка + каналы + устройства
│   ├── 01_ecommerce_funnel.ipynb
│   └── analyze_funnel.py
│
├── 02-ab-test-analysis/
│   ├── dashboard.html                   🧪 Конверсия + стат. значимость
│   ├── 02_ab_test.ipynb
│   └── analyze_ab.py
│
├── 03-churn-prediction/
│   ├── dashboard.html                   🔄 Risk Score + сегменты
│   ├── 03_churn_prediction.ipynb
│   └── analyze_churn.py
│
├── 04-retail-rfm-analysis/
│   ├── dashboard.html                   🛍️ RFM + география + динамика
│   ├── 04_retail_rfm.ipynb
│   ├── online_retail.csv              ← Реальные данные 144K
│   └── analyze_retail.py
│
├── 05-sql-analytics/
│   ├── etl.py                           🗄️ CSV → SQLite (3NF)
│   ├── sql_analytics.py                 📊 12 SQL-запросов с комментариями
│   ├── retail_analytics.db              💾 База данных
│   └── dashboard_sql.png                📈 Визуализация результатов
│
├── 06-etl-pipeline/
│   ├── etl_pipeline.py                  🤖 Полный пайплайн CSV → PDF
│   └── pipeline.py                      ⚡ Обёртка (модульная архитектура)
│
└── 07-advanced-sql/
    ├── advanced_sql.py                  ⚡ 8 оконных функций (NTILE, LAG, etc)
    └── README.md                        # Документация
```

---

**Автор:** Евгений К. + Jack (Hermes Agent)  
**Дата:** 2026-06-01  
**Лицензия:** MIT  
**Версия:** 2.0 (7 проектов)
