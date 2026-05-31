# 📊 Data Analyst Portfolio

> **7 production-ready analytics projects with dashboards, SQL pipelines, and automated reporting.**

---

## 🚀 Quick Start

```bash
git clone https://github.com/jacklivebot-web/data-analyst-portfolio.git
cd data-analyst-portfolio

# Install dependencies
uv venv && uv pip install pandas numpy matplotlib seaborn plotly

# Run any project
python auto_report.py --input data.csv --type funnel --output-dir reports/
```

---

## 📈 Projects Overview

| # | Project | Stack | Status |
|---|---------|-------|--------|
| 1 | [E-commerce Funnel](#-project-1-e-commerce-funnel) | Python, pandas, matplotlib | ✅ |
| 2 | [A/B Test Analysis](#-project-2-ab-test-analysis) | Python, scipy, statistics | ✅ |
| 3 | [Churn Prediction](#-project-3-churn-prediction) | Python, scikit-learn | ✅ |
| 4 | [Retail RFM Analysis](#-project-4-retail-rfm-analysis) | Python, pandas, RFM | ✅ |
| 5 | [SQL Analytics](#-project-5-sql-analytics) | SQLite, CTE, Window Functions | ✅ |
| 6 | [ETL Pipeline](#-project-6-etl-pipeline) | Python, SQLite, automation | ✅ |
| 7 | [Advanced SQL](#-project-7-advanced-sql) | SQLite, NTILE, LAG/LEAD | ✅ |

---

## 📌 Project 1: E-commerce Funnel

**Question:** Where do customers drop off in the purchase journey?

![Funnel Dashboard](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/01-ecommerce-funnel/dashboard_preview.png)

**Key Metrics:**
- Conversion: 2.1% → 8.5% potential
- Main drop-off: 65% abandon at cart
- Mobile vs Desktop: 9.2% vs 11.0%
- Best channel: Referral (11.5%)

**Solution:** Simplify mobile checkout, audit paid social audience.

---

## 📌 Project 2: A/B Test Analysis

**Question:** Is Variant B statistically better than A?

![AB Test Dashboard](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/02-ab-test-analysis/dashboard_preview.png)

**Key Metrics:**
- Conversion: 12.26% → 15.28% (+24.6%)
- p-value < 0.0001, 99% confidence
- ARPU: $10.40 → $13.31 (+28%)
- 95% CI: [14.3%, 16.3%] — no overlap

**Solution:** Roll out Variant B to 100% traffic.

---

## 📌 Project 3: Churn Prediction

**Question:** Who will leave next month? How to save them?

![Churn Dashboard](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/03-churn-prediction/dashboard_preview.png)

**Key Metrics:**
- Model accuracy: 87.2% (ROC-AUC)
- Top-20% Risk Score: 53.5% churn rate
- Free plan churn: 37.8%
- Key signals: >30 days no purchase, declining frequency

**Solution:** Trigger campaigns for high-risk segment.

---

## 📌 Project 4: Retail RFM Analysis

**Question:** Who are the most valuable customers?

*Real data: 144,541 transactions, 2,708 customers, 6 months*

![RFM Dashboard](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/04-retail-rfm-analysis/dashboard_preview.png)

**Key Metrics:**
- Champions (9.8%) = 32% of revenue
- At Risk (9.8%) = 15% of revenue — reactivation needed
- Lost (40%) = 19% of revenue — win-back campaign
- Retention (6 mo): ~20%

**Solution:** VIP program for Champions, reactivation for At Risk/Lost.

---

## 📌 Project 5: SQL Analytics

**Question:** Can we do RFM, cohorts, and funnel analysis in pure SQL?

*144K rows → Normalized SQLite DB (3NF) → 12 analytical queries*

![SQL Dashboard](https://raw.githubusercontent.com/jacklivebot-web/data-analyst-portfolio/master/05-sql-analytics/dashboard_sql.png)

**What was built:**
- **ETL**: CSV → 5 normalized tables (countries, customers, products, orders, order_items)
- **RFM Segmentation** using `NTILE(5)` + `CASE`
- **Cohort Analysis** with retention rates via window functions
- **Moving Average** (`ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`)
- **MoM Growth** with `LAG()` for month-over-month deltas
- **Rankings** (`RANK`, `DENSE_RANK`, `ROW_NUMBER`) within countries

**Key Insight:** 25.9% Champions + 25.4% Lost = clear action matrix.

**Tech:** SQLite, CTEs, window functions, JOINs, subqueries

---

## 📌 Project 6: ETL Pipeline

**Question:** Can we automate the full flow from CSV to report?

**Pipeline:**
```
CSV Input → SQLite (3NF) → SQL Analytics Mart → PNG Dashboard → PDF Report
```

**Features:**
- Automatic schema detection (Retail vs Generic)
- Batch loading (5000 rows/batch for performance)
- Data validation + normalization
- One-command execution: `python pipeline.py --input data.csv`

**Tech:** Python, SQLite, reportlab, matplotlib

---

## 📌 Project 7: Advanced SQL

**Question:** What can advanced window functions reveal?

**8 Advanced Queries:**
1. **NTILE(4)** — quartile-based customer segmentation
2. **LAG + LEAD** — per-customer order dynamics
3. **ROWS BETWEEN** — cumulative revenue + centered moving average
4. **RANK vs DENSE_RANK vs ROW_NUMBER** — ranking comparison
5. **CUME_DIST + PERCENT_RANK** — percentile positioning
6. **FIRST_VALUE / LAST_VALUE** — top/bottom customer per country
7. **RF × F Matrix** — combined Recency-Frequency segmentation
8. **MoM + YoY** — multi-period growth analysis

**Key Insight:** R4F4 segment (fresh + frequent) = VIPs. R1F1 = Sleeping.

**Tech:** SQLite, advanced window functions

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| **Data** | SQL (SQLite, PostgreSQL), pandas, numpy |
| **Analytics** | Statistics, A/B testing, RFM, cohort analysis, ML |
| **Visualization** | matplotlib, seaborn, Plotly, HTML dashboards |
| **Automation** | Python scripts, ETL pipelines, report generation |
| **Environment** | Git, GitHub, uv, Jupyter, Linux |

---

## 📁 Repository Structure

```
data-analyst-portfolio/
├── README.md                          ← This file
├── auto_report.py                     🤖 CSV → Dashboard + PDF (automated)
├── dashboards.py                        # Interactive HTML dashboard generator
│
├── 01-ecommerce-funnel/
│   ├── dashboard.html                   🎯 Interactive funnel + channels
│   ├── dashboard_preview.png            📊 Static preview
│   ├── 01_ecommerce_funnel.ipynb        📓 Jupyter notebook
│   └── analyze_funnel.py              🔧 Python analysis script
│
├── 02-ab-test-analysis/
│   ├── dashboard.html                   🧪 Statistical significance dashboard
│   ├── dashboard_preview.png            📊 Static preview
│   ├── 02_ab_test.ipynb               📓 Jupyter notebook
│   └── analyze_ab.py                  🔧 Python analysis script
│
├── 03-churn-prediction/
│   ├── dashboard.html                   🔄 Risk score + segments
│   ├── dashboard_preview.png            📊 Static preview
│   ├── 03_churn_prediction.ipynb      📓 Jupyter notebook
│   └── analyze_churn.py               🔧 Python analysis script
│
├── 04-retail-rfm-analysis/
│   ├── dashboard.html                   🛍️ RFM + geography + dynamics
│   ├── dashboard_preview.png            📊 Static preview
│   ├── online_retail.csv              💾 Real data (144K rows)
│   ├── 04_retail_rfm.ipynb            📓 Jupyter notebook
│   └── analyze_retail.py              🔧 Python analysis script
│
├── 05-sql-analytics/
│   ├── etl.py                           🗄️ CSV → SQLite (3NF normalization)
│   ├── sql_analytics.py               📊 12 SQL queries with comments
│   ├── retail_analytics.db            💾 SQLite database
│   └── dashboard_sql.png              📈 SQL results visualization
│
├── 06-etl-pipeline/
│   ├── etl_pipeline.py                  🤖 Full pipeline CSV → PDF
│   └── pipeline.py                      ⚡ Modular wrapper
│
└── 07-advanced-sql/
    ├── advanced_sql.py                  ⚡ 8 advanced window function queries
    └── README.md                        # Documentation
```

---

## 📄 PDF Reports

Two ready-to-use PDF presentations are included:

| Report | Pages | Purpose |
|--------|-------|---------|
| `Data_Analyst_Portfolio_Report.pdf` | 8 | Portfolio presentation with all dashboards |
| `Executive_Summary_Report.pdf` | 7 | Business report for stakeholders (metrics + ROI) |

---

## ⚡ Automation

**Auto-Report Generator:**
```bash
# Funnel analysis
python auto_report.py --input funnel.csv --type funnel --output-dir reports/

# A/B test report
python auto_report.py --input ab_test.csv --type ab_test --output-dir reports/

# Churn prediction
python auto_report.py --input customers.csv --type churn --output-dir reports/

# RFM segmentation
python auto_report.py --input retail.csv --type rfm --output-dir reports/
```

**Output:** `dashboard_TYPE.png` + `dashboard_TYPE.html` + `auto_report_TYPE.pdf`

---

## 🎯 Business Questions Answered

1. **Where do we lose customers?** → Funnel analysis with device/channel breakdown
2. **Which variant wins?** → Statistical A/B test with confidence intervals
3. **Who will churn?** → ML model with 87% accuracy + risk scoring
4. **Who brings the money?** → RFM segmentation with VIP identification
5. **Can SQL handle it all?** → 20+ queries proving analytical SQL power
6. **Can it be automated?** → One-command ETL pipeline
7. **What do window functions show?** → Advanced segmentation matrices

---

**License:** MIT  
**Last Updated:** 2026-06-01
