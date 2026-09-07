# Nassau-Candy-Profitability-Analysis
Product Line Profitability &amp; Margin Performance Analysis for Nassau Candy Distributor using Python, Pandas, Seaborn and Streamlit.
# 🍫 Nassau Candy Distributor
## Product Line Profitability & Margin Performance Analysis

### 📌 Project Overview

This project analyzes product-level profitability and margin performance for Nassau Candy Distributor.

The objective is to identify profitable products, low-margin products, high-cost products, division-level performance, and potential margin risks using data-driven analysis.

### 🎯 Business Problem

Sales volume alone does not indicate profitability. Some products may have high sales but generate relatively low margins.

This analysis provides visibility into:

- Products generating the highest gross profit
- Products with the highest gross margins
- High-sales and low-margin products
- Low-sales and low-profit products
- Division-level profitability
- Cost-heavy products
- Profit concentration and dependency risks

### 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Jupyter Notebook
- Streamlit

### 📊 Dataset

The dataset contains order, customer, product, sales, cost and profit information.

Important fields include:

- Order Date
- Ship Date
- Division
- Region
- Product ID
- Product Name
- Sales
- Units
- Gross Profit
- Cost

### 🧹 Data Cleaning & Validation

The following checks were performed:

- Missing-value analysis
- Duplicate-record validation
- Sales validation
- Cost validation
- Units validation
- Gross Profit validation
- Date conversion
- Product and division analysis

### 📈 Key Performance Indicators

#### Gross Margin (%)

Gross Margin = Gross Profit / Sales × 100

#### Profit per Unit

Profit per Unit = Gross Profit / Units

#### Revenue Contribution

Revenue Contribution = Product Sales / Total Sales

#### Profit Contribution

Profit Contribution = Product Profit / Total Profit

#### Margin Volatility

Margin volatility measures the variation in gross margin over time.

### 🔎 Analysis Performed

#### Product-Level Analysis

- Product profitability ranking
- Gross margin ranking
- Gross profit comparison
- Profit per unit
- High-sales/low-margin identification
- Low-sales/low-profit identification

#### Division-Level Analysis

- Sales by division
- Gross profit by division
- Gross margin by division
- Revenue vs profit comparison

#### Pareto Analysis

Profit concentration was analyzed to identify products contributing the majority of total profit and potential dependency risks.

#### Cost Diagnostics

Cost vs sales analysis was performed to identify cost-heavy and margin-poor products.

### 📊 Streamlit Dashboard

The project includes an interactive Streamlit dashboard with:

- Product profitability overview
- Product margin leaderboard
- Division performance analysis
- Cost vs margin diagnostics
- Pareto analysis
- Margin risk identification

### 🔍 Dashboard Filters

Users can interact with:

- Date range selector
- Division filter
- Product filter
- Minimum gross margin slider
- Product search

### 💡 Business Insights

The analysis helps management:

- Identify high-profit products
- Review low-margin products
- Improve pricing decisions
- Control product costs
- Identify products requiring cost renegotiation
- Evaluate products for rationalization
- Reduce dependency on a small number of products

### 📁 Project Files

- `Nassau Candy Distributor.csv` — Original dataset
- `Nassau_Candy_Cleaned.csv` — Cleaned dataset
- `app.py` — Streamlit dashboard
- `Nassau_Candy_Profitability_Analysis.ipynb` — Data analysis notebook

### 🚀 How to Run the Dashboard

Install the required libraries:

```bash
pip install pandas numpy matplotlib seaborn streamlit
