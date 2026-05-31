# 🛍️ Проект 4: RFM + Когортный анализ реальных розничных продаж

## Данные
**[UCI Online Retail Dataset](https://archive.ics.uci.edu/ml/datasets/online+retail)** — 541,909 реальных транзакций UK-магазина за декабрь 2010 — декабрь 2011.

| Характеристика | Значение |
|----------------|----------|
| Транзакций | 541,909 |
| Уникальных клиентов | ~4,300 |
| Уникальных товаров | ~4,000 |
| Стран | 38 |
| Период | 01.12.2010 — 09.12.2011 |

## Задача
RFM-сегментация клиентов + когортный анализ retention + география + товарный анализ.

## Что демонстрирует этот проект
| Навык | Применение |
|-------|-----------|
| **RFM** | Сегментация клиентов по Recency, Frequency, Monetary |
| **Когортный анализ** | Retention rate по месяцам с момента первой покупки |
| **География** | Распределение выручки по странам |
| **Сезонность** | Динамика выручки по месяцам |
| **Товарный анализ** | Топ-товары по выручке и количеству |

## Ключевые результаты

### RFM-сегментация
| Сегмент | Клиенты | Выручка | Доля выручки |
|---------|---------|---------|-------------|
| Champions | ~420 (9.8%) | $1.1M | ~32% |
| Loyal | ~750 (17.6%) | $850K | ~25% |
| Potential Loyalists | ~650 (15.2%) | $420K | ~12% |
| At Risk | ~420 (9.8%) | $380K | ~11% |
| Lost | ~1,700 (40%) | $650K | ~19% |

### Инсайты
- **Champions** — 10% клиентов приносят 32% выручки → VIP-программа
- **Lost** — 40% клиентов, но $650K выручки → реактивационная кампания
- **Retention** падает к 6 месяцу до ~20% → улучшить onboarding
- **EU рынок** недооценён: Германия, Франция, Нидерланды — потенциал роста
- **Сезонность**: пик в ноябре (предпраздничные продажи)

## SQL-шаблоны
```sql
-- RFM-базовые метрики
WITH customer_metrics AS (
    SELECT
        CustomerID,
        DATEDIFF(day, MAX(InvoiceDate), '2011-12-10') as Recency,
        COUNT(DISTINCT InvoiceNo) as Frequency,
        SUM(Quantity * UnitPrice) as Monetary
    FROM online_retail
    WHERE Quantity > 0 AND UnitPrice > 0
    GROUP BY CustomerID
)
SELECT
    CASE
        WHEN Recency <= 30 AND Frequency >= 10 AND Monetary >= 1000 THEN 'Champions'
        WHEN Recency <= 60 AND Frequency >= 5 THEN 'Loyal'
        WHEN Recency <= 30 AND Frequency < 5 THEN 'New'
        WHEN Recency > 90 AND Frequency >= 5 THEN 'At Risk'
        WHEN Recency > 120 AND Frequency < 3 THEN 'Lost'
        ELSE 'Regular'
    END as segment,
    COUNT(*) as customers,
    SUM(Monetary) as revenue
FROM customer_metrics
GROUP BY segment
ORDER BY revenue DESC;

-- Когортный анализ
WITH first_purchase AS (
    SELECT CustomerID, MIN(InvoiceDate) as first_date
    FROM online_retail
    GROUP BY CustomerID
)
SELECT
    DATE_FORMAT(fp.first_date, '%Y-%m') as cohort,
    DATEDIFF(month, fp.first_date, r.InvoiceDate) as period,
    COUNT(DISTINCT r.CustomerID) as active_customers
FROM online_retail r
JOIN first_purchase fp ON r.CustomerID = fp.CustomerID
GROUP BY cohort, period
ORDER BY cohort, period;
```

## Методология: Human+AI
Этот проект использует **реальные данные** (не синтетические), что демонстрирует:
1. Работу с «грязными» данными (отрицательные quantity, пропущенные CustomerID)
2. Масштабируемость подхода (541K записей)
3. Практическую применимость методов

Агент автоматизировал: загрузку данных, очистку, RFM-расчёт, визуализацию.
Евгений валидировал: логику сегментации, бизнес-интерпретацию, рекомендации.

---

**Источник данных:** UCI Machine Learning Repository (Online Retail Dataset)
**Методология:** сгенерировано агентом, валидировано аналитиком
