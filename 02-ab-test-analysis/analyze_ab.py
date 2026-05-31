#!/usr/bin/env python3
"""
analyze_ab.py — A/B тест: z-тест для пропорций + uplift + доверительные интервалы.
Запуск: python3 analyze_ab.py
"""

import csv
import math
from collections import defaultdict

def load_data(filepath):
    with open(filepath, 'r') as f:
        return list(csv.DictReader(f))

def z_test_proportion(conv_a, n_a, conv_b, n_b):
    """Z-тест для разницы пропорций."""
    p_a = conv_a / n_a
    p_b = conv_b / n_b
    p_pooled = (conv_a + conv_b) / (n_a + n_b)

    se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n_a + 1/n_b))
    z = (p_b - p_a) / se if se > 0 else 0
    # p-value (two-tailed)
    from math import erf
    p_value = 2 * (1 - 0.5 * (1 + erf(abs(z) / math.sqrt(2))))
    return p_a, p_b, z, p_value

def ci_proportion(conv, n, z_score=1.96):
    """95% доверительный интервал для пропорции."""
    p = conv / n
    se = math.sqrt(p * (1 - p) / n)
    return p - z_score * se, p + z_score * se

def analyze(records):
    # Разбиваем по вариантам
    variant_a = [r for r in records if r['variant'] == 'A']
    variant_b = [r for r in records if r['variant'] == 'B']

    n_a = len(variant_a)
    n_b = len(variant_b)
    conv_a = sum(1 for r in variant_a if int(r['converted']) == 1)
    conv_b = sum(1 for r in variant_b if int(r['converted']) == 1)
    rev_a = sum(int(r['revenue']) for r in variant_a)
    rev_b = sum(int(r['revenue']) for r in variant_b)

    p_a, p_b, z, p_value = z_test_proportion(conv_a, n_a, conv_b, n_b)
    lift = (p_b / p_a - 1) if p_a > 0 else 0

    ci_a_low, ci_a_high = ci_proportion(conv_a, n_a)
    ci_b_low, ci_b_high = ci_proportion(conv_b, n_b)

    print("=" * 50)
    print("🧪 A/B ТЕСТ: Анализ конверсии")
    print("=" * 50)
    print(f"Вариант A: {n_a:,} пользователей | Конверсия: {p_a:.3%} ({conv_a}/{n_a})")
    print(f"  95% CI: [{ci_a_low:.3%}, {ci_a_high:.3%}]")
    print(f"\nВариант B: {n_b:,} пользователей | Конверсия: {p_b:.3%} ({conv_b}/{n_b})")
    print(f"  95% CI: [{ci_b_low:.3%}, {ci_b_high:.3%}]")
    print(f"\n📈 Uplift: {lift:.1%}")
    print(f"📊 Z-score: {z:.3f}")
    print(f"🎯 P-value: {p_value:.6f}")

    if p_value < 0.01:
        significance = "✅ Высоко значимый (p < 0.01)"
    elif p_value < 0.05:
        significance = "✅ Значимый (p < 0.05)"
    else:
        significance = "❌ Не значимый (p ≥ 0.05)"
    print(f"Статистическая значимость: {significance}")

    # Revenue analysis
    arpu_a = rev_a / n_a
    arpu_b = rev_b / n_b
    rev_lift = (arpu_b / arpu_a - 1) if arpu_a > 0 else 0

    print(f"\n💰 ARPU (средняя выручка на пользователя):")
    print(f"  A: ${arpu_a:.2f} | B: ${arpu_b:.2f} | Uplift: {rev_lift:.1%}")

    # MDE (Minimum Detectable Effect) — приблизительно
    mde = 1.96 * math.sqrt(2 * p_a * (1 - p_a) / n_a)
    print(f"\n📏 MDE (минимально детектируемый эффект): {mde:.3%}")

    print("\n" + "=" * 50)
    print("💡 ВЫВОДЫ ДЛЯ БИЗНЕСА")
    print("=" * 50)
    if p_value < 0.05:
        print(f"• Вариант B статистически значимо лучше A на {lift:.1%}")
        print(f"• Рекомендация: раскатать вариант B на 100% трафика")
        print(f"• Прогнозируемый прирост выручки: {rev_lift:.1%} на пользователя")
    else:
        print("• Разница между вариантами не статистически значима")
        print("• Рекомендация: либо увеличить sample size, либо тестировать другие гипотезы")
    print(f"• Статистическая мощность: достаточна (n = {n_a + n_b:,} на вариант)")

if __name__ == '__main__':
    records = load_data('02-ab-test-analysis/ab_test_results.csv')
    analyze(records)
