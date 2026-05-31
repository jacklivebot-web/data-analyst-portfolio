# 🛒 Проект 1: Воронка продаж E-commerce

## Концепция: Augmented Analyst в действии

Этот проект демонстрирует, как аналитик + ИИ-агент решают задачу в 3–5 раз быстрее классического подхода.

### Задача
Понять, где в воронке теряются пользователи и какой канал/устройство приносит больше денег.

### Данные
- 5,000 пользователей за 30 дней
- События: `view_product` → `add_to_cart` → `purchase`
- Атрибуты: канал привлечения, устройство, выручка

### Что классический аналитик делает 4 часа
1. Пишет SQL-запросы для подсчёта конверсий по шагам
2. Считает в Excel/Python группировки по каналам
3. Строит графики вручную
4. Пишет выводы для бизнеса

### Что делает Augmented Analyst (мы) за 40 минут
1. **Агент-генератор данных** — создаёт реалистичный датасет с заданной логикой конверсии
2. **Параллельные агенты-анализаторы**:
   - Агент SQL: генерирует оптимальные запросы для воронки
   - Агент Python: считает метрики и строит графики
   - Агент интерпретации: формулирует бизнес-выводы на русском
3. **Евгений**: проверяет логику, задаёт уточняющие вопросы, принимает решение

### Ключевые метрики
| Метрика | Значение |
|---------|----------|
| Всего регистраций | 5,000 |
| Просмотрели товар | ~80% |
| Добавили в корзину | ~32% от просмотревших |
| Купили | ~8% от просмотревших |
| Средний чек | ~$130 |

### SQL-шаблоны для анализа
```sql
-- Воронка по шагам
WITH funnel AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_type = 'view_product' THEN 1 ELSE 0 END) as viewed,
        MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) as carted,
        MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchased
    FROM funnel_events
    GROUP BY user_id
)
SELECT
    SUM(viewed) as users_viewed,
    SUM(carted) as users_carted,
    SUM(purchased) as users_purchased,
    ROUND(100.0 * SUM(carted) / SUM(viewed), 2) as cart_rate,
    ROUND(100.0 * SUM(purchased) / SUM(viewed), 2) as purchase_rate
FROM funnel;

-- Конверсия по каналам
SELECT
    channel,
    COUNT(DISTINCT user_id) as total_users,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as buyers,
    ROUND(100.0 * buyers / total_users, 2) as conversion_rate,
    SUM(revenue) as total_revenue
FROM funnel_events
GROUP BY channel
ORDER BY conversion_rate DESC;
```

### Инсайты (примерные)
- **Mobile vs Desktop**: мобильные пользователи конвертируют хуже — возможно, проблема в UX оформления заказа
- **Канал `paid_social`**: высокий трафик, но низкая конверсия — проверить качество аудитории
- **Канал `organic`**: лучшая конверсия и LTV — инвестировать в SEO/контент

---

**Методология:** сгенерировано агентом, валидировано аналитиком, документировано в Obsidian Vault.
