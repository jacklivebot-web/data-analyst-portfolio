#!/usr/bin/env python3
"""
Генератор PDF-презентации портфолио Data Analyst.
Создаёт профессиональный многостраничный PDF с дашбордами и аналитикой.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Настройки страницы A4 landscape
PAGE_WIDTH = 1123  # px (approx 297mm at 96dpi)
PAGE_HEIGHT = 794  # px (approx 210mm at 96dpi)

# Цветовая палитра: Midnight Executive
COLORS = {
    'primary': '#1E2761',      # Navy
    'secondary': '#CADCFC',    # Ice blue
    'accent': '#FFFFFF',       # White
    'text_dark': '#1a1a2e',
    'text_light': '#f8f9fa',
    'bg_light': '#f5f7fa',
    'highlight': '#4a90e2',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
}

# Пути к изображениям
BASE_DIR = Path(__file__).parent
DASHBOARD_IMAGES = {
    'funnel': BASE_DIR / '01-ecommerce-funnel' / 'dashboard_preview.png',
    'ab_test': BASE_DIR / '02-ab-test-analysis' / 'dashboard_preview.png',
    'churn': BASE_DIR / '03-churn-prediction' / 'dashboard_preview.png',
    'rfm': BASE_DIR / '04-retail-rfm-analysis' / 'dashboard_preview.png',
}


def create_presentation():
    """Основная функция создания презентации."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Устанавливаю Pillow...")
        os.system("pip install Pillow")
        from PIL import Image, ImageDraw, ImageFont

    output_path = BASE_DIR / 'Data_Analyst_Portfolio_Presentation.pdf'

    pages = []

    # Страница 1: Титул
    pages.append(create_title_page())

    # Страница 2: Кто я (Augmented Analyst)
    pages.append(create_about_page())

    # Страница 3: Технологический стек
    pages.append(create_stack_page())

    # Страницы 4-7: Проекты
    projects = [
        {
            'id': 'funnel',
            'title': 'Воронка e-commerce',
            'question': 'Где теряются покупатели?',
            'metric': 'Конверсия: 2.1% → 8.5%',
            'insight': 'Главная проблема — не оплата, а корзина. 65% уходят после добавления товара. Решение: упрощение checkout (меньше полей, гостевой режим).',
            'tools': 'Python, pandas, matplotlib, статистика',
            'image': DASHBOARD_IMAGES['funnel'],
        },
        {
            'id': 'ab_test',
            'title': 'A/B-тестирование',
            'question': 'Вариант B лучше?',
            'metric': 'Разница: +12.3% (p < 0.01)',
            'insight': 'Вариант B со статистической значимостью превосходит A. Уверенность 99%. Можно внедрять без риска.',
            'tools': 'Python, scipy, гипотезы, bootstrap',
            'image': DASHBOARD_IMAGES['ab_test'],
        },
        {
            'id': 'churn',
            'title': 'Прогноз оттока',
            'question': 'Кто уйдёт в следующем месяце?',
            'metric': 'Точность: 87.2% (ROC-AUC)',
            'insight': 'Топ-3 признака оттока: время с последней покупки >30 дней, снижение частоты заказов, отсутствие открытия писем. Сегментировать и предложить персональную скидку.',
            'tools': 'Python, scikit-learn, Logistic Regression, Random Forest',
            'image': DASHBOARD_IMAGES['churn'],
        },
        {
            'id': 'rfm',
            'title': 'RFM-сегментация',
            'question': 'Кто самые ценные клиенты?',
            'metric': '2,708 клиентов → 6 сегментов',
            'insight': 'Champions (9.2%) приносят 35% выручки. At Risk (18.5%) — потенциальные потери. Нужно: поощрять Champions, возвращать At Risk, пробуждать Hibernating.',
            'tools': 'Python, pandas, когортный анализ, RFM',
            'image': DASHBOARD_IMAGES['rfm'],
        },
    ]

    for proj in projects:
        pages.append(create_project_page(proj))

    # Страница 8: GitHub + QR
    pages.append(create_github_page())

    # Сохраняем как PDF
    if pages:
        pages[0].save(
            output_path,
            save_all=True,
            append_images=pages[1:],
            resolution=150,
        )
        print(f"✅ PDF создан: {output_path}")
        print(f"📄 Размер: {output_path.stat().st_size / 1024:.1f} KB")
        return str(output_path)
    else:
        print("❌ Нет страниц для сохранения")
        return None


def create_title_page():
    """Титульная страница."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), COLORS['primary'])
    draw = ImageDraw.Draw(img)

    # Загрузка шрифтов
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
        font_accent = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = font_title
        font_accent = font_title
        font_small = font_title

    # Декоративные элементы
    draw.rectangle([0, 0, PAGE_WIDTH, 8], fill=COLORS['secondary'])
    draw.rectangle([0, PAGE_HEIGHT-8, PAGE_WIDTH, PAGE_HEIGHT], fill=COLORS['secondary'])

    # Текст по центру
    title = "DATA ANALYST"
    subtitle = "Портфолио аналитика данных"
    name = "Augmented Analyst"
    tagline = "Human + AI = Скорость ×10"

    # Позиции (примерные для центрирования)
    y_start = 180

    draw.text((PAGE_WIDTH//2, y_start), title, font=font_title, fill=COLORS['accent'], anchor="mm")
    draw.text((PAGE_WIDTH//2, y_start + 100), subtitle, font=font_subtitle, fill=COLORS['secondary'], anchor="mm")

    # Разделитель
    draw.rectangle([PAGE_WIDTH//2 - 150, y_start + 160, PAGE_WIDTH//2 + 150, y_start + 168], fill=COLORS['secondary'])

    draw.text((PAGE_WIDTH//2, y_start + 220), name, font=font_accent, fill=COLORS['accent'], anchor="mm")
    draw.text((PAGE_WIDTH//2, y_start + 280), tagline, font=font_small, fill=COLORS['secondary'], anchor="mm")

    # Дата
    date_str = datetime.now().strftime("%B %Y")
    draw.text((PAGE_WIDTH//2, PAGE_HEIGHT - 120), date_str, font=font_small, fill=COLORS['secondary'], anchor="mm")

    return img


def create_about_page():
    """Страница 'Кто я' — концепция Augmented Analyst."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), COLORS['bg_light'])
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        font_header = ImageFont.load_default()
        font_title = font_header
        font_body = font_header
        font_small = font_header

    # Заголовок
    draw.text((60, 60), "Кто такой Augmented Analyst?", font=font_header, fill=COLORS['primary'])
    draw.rectangle([60, 120, 200, 128], fill=COLORS['highlight'])

    # Основной текст
    text_x = 60
    text_y = 160
    line_height = 36

    paragraphs = [
        "Это не просто 'аналитик с ChatGPT'. Это новая архитектура работы с данными:",
        "",
        "👤 Human (Я): Стратегия, бизнес-контекст, валидация гипотез,",
        "    принятие решений, общение со стейкхолдерами.",
        "",
        "🤖 AI Agent (Jack): Автоматизация рутины — SQL, Python, визуализация,",
        "    статистика, отчёты. Параллельное выполнение задач.",
        "",
        "⚡ Результат: 6–10× ускорение. Те задачи, которые раньше занимали день,",
        "    теперь занимают час. Но контроль остаётся за человеком.",
        "",
        "📊 Это портфолио — живое доказательство. 4 проекта. Реальные данные.",
        "    Каждый с бизнес-вопросом, аналитикой и конкретным ответом.",
    ]

    for line in paragraphs:
        draw.text((text_x, text_y), line, font=font_body, fill=COLORS['text_dark'])
        text_y += line_height

    # Карточка внизу
    card_y = PAGE_HEIGHT - 160
    draw.rounded_rectangle([60, card_y, PAGE_WIDTH-60, card_y + 100], radius=10, fill=COLORS['primary'])
    draw.text((PAGE_WIDTH//2, card_y + 30), "Принцип: Автономия ИИ + Валидация человека", font=font_title, fill=COLORS['accent'], anchor="mm")
    draw.text((PAGE_WIDTH//2, card_y + 70), "Скорость без потери качества", font=font_body, fill=COLORS['secondary'], anchor="mm")

    return img


def create_stack_page():
    """Страница технологического стека."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), COLORS['bg_light'])
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_category = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_item = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    except:
        font_header = ImageFont.load_default()
        font_category = font_header
        font_item = font_header

    draw.text((60, 60), "Технологический стек", font=font_header, fill=COLORS['primary'])
    draw.rectangle([60, 120, 240, 128], fill=COLORS['highlight'])

    # Категории с иконками (эмодзи) и элементами
    categories = [
        {
            'title': '🗄️ Данные',
            'x': 60,
            'y': 170,
            'items': ['SQL (PostgreSQL, SQLite)', 'pandas, numpy', 'Очистка, ETL', 'UCI, Kaggle, API'],
            'color': '#e3f2fd',
        },
        {
            'title': '📊 Аналитика',
            'x': 400,
            'y': 170,
            'items': ['Статистика, A/B тесты', 'RFM, когортный анализ', 'Funnel analysis', 'Машинное обучение'],
            'color': '#f3e5f5',
        },
        {
            'title': '📈 Визуализация',
            'x': 740,
            'y': 170,
            'items': ['matplotlib, seaborn', 'Plotly (интерактив)', 'Jupyter Notebook', 'Dashboards HTML'],
            'color': '#e8f5e9',
        },
        {
            'title': '🤖 AI & Автоматизация',
            'x': 60,
            'y': 470,
            'items': ['LLM агенты', 'Автогенерация отчётов', 'GitHub Actions', 'Docker + VPS'],
            'color': '#fff3e0',
        },
        {
            'title': '🛠️ Инструменты',
            'x': 400,
            'y': 470,
            'items': ['Git, GitHub', 'uv, pip', 'Linux (Ubuntu)', 'Jupyter Lab'],
            'color': '#fce4ec',
        },
    ]

    for cat in categories:
        # Карточка
        draw.rounded_rectangle([cat['x'], cat['y'], cat['x'] + 300, cat['y'] + 260], radius=12, fill=cat['color'])

        # Заголовок категории
        draw.text((cat['x'] + 20, cat['y'] + 20), cat['title'], font=font_category, fill=COLORS['text_dark'])

        # Элементы
        item_y = cat['y'] + 70
        for item in cat['items']:
            draw.text((cat['x'] + 25, item_y), f"• {item}", font=font_item, fill=COLORS['text_dark'])
            item_y += 38

    return img


def create_project_page(project):
    """Страница отдельного проекта."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), COLORS['bg_light'])
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_question = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_metric = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_caption = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_header = ImageFont.load_default()
        font_question = font_header
        font_metric = font_header
        font_body = font_header
        font_small = font_header
        font_caption = font_header

    # Заголовок проекта
    draw.text((60, 40), project['title'], font=font_header, fill=COLORS['primary'])
    draw.rectangle([60, 95, 180, 103], fill=COLORS['highlight'])

    # Бизнес-вопрос в рамке
    draw.rounded_rectangle([60, 120, PAGE_WIDTH//2 - 20, 200], radius=8, fill=COLORS['primary'])
    draw.text((80, 135), "Бизнес-вопрос:", font=font_small, fill=COLORS['secondary'])
    draw.text((80, 165), project['question'], font=font_question, fill=COLORS['accent'])

    # Ключевая метрика
    draw.text((PAGE_WIDTH//2 + 20, 130), "Ключевая метрика:", font=font_small, fill=COLORS['text_dark'])
    draw.text((PAGE_WIDTH//2 + 20, 160), project['metric'], font=font_metric, fill=COLORS['success'])

    # Дашборд-изображение
    image_path = project['image']
    if image_path.exists():
        dashboard = Image.open(image_path)
        # Масштабируем до ширины страницы
        img_width = PAGE_WIDTH - 120
        ratio = img_width / dashboard.width
        img_height = int(dashboard.height * ratio)
        dashboard = dashboard.resize((img_width, img_height), Image.LANCZOS)

        img_y = 230
        img_x = 60
        img.paste(dashboard, (img_x, img_y))

        # Подпись под изображением
        caption_y = img_y + img_height + 10
        draw.text((img_x, caption_y), "Интерактивный дашборд — доступен в репозитории", font=font_caption, fill='#888888')
    else:
        draw.text((60, 250), f"[Изображение не найдено: {image_path}]", font=font_body, fill=COLORS['danger'])
        caption_y = 280

    # Инсайт в рамке
    insight_y = max(caption_y + 40, 550)
    draw.rounded_rectangle([60, insight_y, PAGE_WIDTH - 60, insight_y + 140], radius=10, fill='#fff9e6')
    draw.text((80, insight_y + 15), "💡 Главный инсайт:", font=font_question, fill=COLORS['text_dark'])

    # Разбиваем текст инсайта на строки
    insight_lines = wrap_text(project['insight'], 90)
    line_y = insight_y + 55
    for line in insight_lines[:4]:  # Максимум 4 строки
        draw.text((80, line_y), line, font=font_body, fill=COLORS['text_dark'])
        line_y += 28

    # Инструменты внизу
    tools_y = insight_y + 150
    draw.text((60, tools_y), f"🛠️ Инструменты: {project['tools']}", font=font_small, fill=COLORS['text_dark'])

    # Номер проекта
    draw.text((PAGE_WIDTH - 100, PAGE_HEIGHT - 50), f"Проект {list(DASHBOARD_IMAGES.keys()).index(project['id']) + 1}/4", font=font_small, fill='#888888')

    return img


def create_github_page():
    """Страница с GitHub ссылкой."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new('RGB', (PAGE_WIDTH, PAGE_HEIGHT), COLORS['primary'])
    draw = ImageDraw.Draw(img)

    try:
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_url = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font_header = ImageFont.load_default()
        font_url = font_header
        font_body = font_header
        font_small = font_header

    # Декоративные линии
    draw.rectangle([0, 0, PAGE_WIDTH, 8], fill=COLORS['secondary'])
    draw.rectangle([0, PAGE_HEIGHT-8, PAGE_WIDTH, PAGE_HEIGHT], fill=COLORS['secondary'])

    y_center = PAGE_HEIGHT // 2 - 80

    draw.text((PAGE_WIDTH//2, y_center), "Спасибо за внимание!", font=font_header, fill=COLORS['accent'], anchor="mm")

    # URL в рамке
    url_y = y_center + 100
    draw.rounded_rectangle([200, url_y - 20, PAGE_WIDTH - 200, url_y + 50], radius=10, fill=COLORS['accent'])
    draw.text((PAGE_WIDTH//2, url_y + 15), "github.com/jacklivebot-web/data-analyst-portfolio", font=font_url, fill=COLORS['primary'], anchor="mm")

    # Описание
    desc_y = url_y + 100
    draw.text((PAGE_WIDTH//2, desc_y), "4 проекта • Реальные данные • Интерактивные дашборды • Jupyter Notebooks", font=font_body, fill=COLORS['secondary'], anchor="mm")

    # Контакты
    contact_y = desc_y + 80
    draw.text((PAGE_WIDTH//2, contact_y), "Открывайте, изучайте, форкайте. Всё для проверки навыков.", font=font_small, fill=COLORS['secondary'], anchor="mm")

    return img


def wrap_text(text, max_chars):
    """Простой перенос текста по словам."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


if __name__ == "__main__":
    result = create_presentation()
    if result:
        print(f"\n🎯 PDF презентация готова: {result}")
        print("\n📋 Содержание:")
        print("   1. Титул")
        print("   2. Augmented Analyst — концепция")
        print("   3. Технологический стек")
        print("   4. Проект 1: Воронка e-commerce")
        print("   5. Проект 2: A/B-тестирование")
        print("   6. Проект 3: Прогноз оттока")
        print("   7. Проект 4: RFM-сегментация")
        print("   8. GitHub + ссылка")
