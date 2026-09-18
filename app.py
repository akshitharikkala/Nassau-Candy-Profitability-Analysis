import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Nassau Candy Profitability Dashboard",
    page_icon="🍬",
    layout="wide"
)


# ---------------------------------------------------------
# TITLE
# ---------------------------------------------------------
st.title("🍬 Nassau Candy Distributor")
st.subheader("Product Line Profitability & Margin Performance Analysis")

st.write(
    "Interactive dashboard for analyzing sales, cost, gross profit, "
    "gross margin, product performance, division performance, and cost risks."
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
DATA_FILE = Path("Nassau_Candy_Cleaned.csv")

if not DATA_FILE.exists():
    st.error(
        "Nassau_Candy_Cleaned.csv was not found. "
        "Make sure the CSV file is in the same folder as app.py."
    )
    st.stop()

df = pd.read_csv(DATA_FILE)


# ---------------------------------------------------------
# DATA PREPARATION
# ---------------------------------------------------------
required_columns = [
    "Order Date",
    "Division",
    "Product ID",
    "Product Name",
    "Sales",
    "Units",
    "Gross Profit",
    "Cost"
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()


df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")

numeric_columns = ["Sales", "Units", "Gross Profit", "Cost"]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["Order Date", "Sales", "Units", "Gross Profit", "Cost"])


# Calculate metrics if they are not already available
df["Gross Margin(%)"] = np.where(
    df["Sales"] != 0,
    (df["Gross Profit"] / df["Sales"]) * 100,
    0
)

df["Profit per Unit"] = np.where(
    df["Units"] != 0,
    df["Gross Profit"] / df["Units"],
    0
)


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("🔎 Dashboard Filters")

# Division filter
division_options = sorted(df["Division"].dropna().unique().tolist())

selected_divisions = st.sidebar.multiselect(
    "Select Division",
    options=division_options,
    default=division_options
)


# Product filter
product_options = sorted(df["Product Name"].dropna().unique().tolist())

selected_products = st.sidebar.multiselect(
    "Select Product",
    options=product_options,
    default=product_options
)


# Date filter
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# Margin threshold
margin_threshold = st.sidebar.slider(
    "Minimum Gross Margin (%)",
    min_value=0.0,
    max_value=100.0,
    value=50.0,
    step=1.0
)


# Product search
product_search = st.sidebar.text_input(
    "Search Product",
    placeholder="Type product name..."
)


# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------
filtered_df = df.copy()

if selected_divisions:
    filtered_df = filtered_df[
        filtered_df["Division"].isin(selected_divisions)
    ]

if selected_products:
    filtered_df = filtered_df[
        filtered_df["Product Name"].isin(selected_products)
    ]


if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["Order Date"] >= start_date)
        & (filtered_df["Order Date"] <= end_date)
    ]


if product_search:
    filtered_df = filtered_df[
        filtered_df["Product Name"]
        .str.contains(product_search, case=False, na=False)
    ]


# ---------------------------------------------------------
# HEADER INFORMATION
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Gross Profit"].sum()
total_cost = filtered_df["Cost"].sum()
total_units = filtered_df["Units"].sum()

overall_margin = (
    total_profit / total_sales * 100
    if total_sales != 0
    else 0
)

with col1:
    st.metric(
        "Total Sales",
        f"${total_sales:,.0f}"
    )

with col2:
    st.metric(
        "Gross Profit",
        f"${total_profit:,.0f}"
    )

with col3:
    st.metric(
        "Gross Margin",
        f"{overall_margin:.2f}%"
    )

with col4:
    st.metric(
        "Units Sold",
        f"{total_units:,.0f}"
    )


st.divider()


# ---------------------------------------------------------
# DATASET INFORMATION
# ---------------------------------------------------------
with st.expander("📋 Dataset Information"):
    info_col1, info_col2, info_col3 = st.columns(3)

    with info_col1:
        st.write("**Filtered Records:**", f"{len(filtered_df):,}")

    with info_col2:
        st.write(
            "**Products:**",
            filtered_df["Product Name"].nunique()
        )

    with info_col3:
        st.write(
            "**Divisions:**",
            filtered_df["Division"].nunique()
        )


# ---------------------------------------------------------
# DOWNLOAD FILTERED DATA
# ---------------------------------------------------------
csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Dataset",
    data=csv_data,
    file_name="Nassau_Candy_Filtered_Data.csv",
    mime="text/csv"
)


# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Overview",
        "🍫 Product Analysis",
        "🏢 Division Analysis",
        "⚠️ Risk Analysis",
        "📈 Pareto Analysis"
    ]
)


# =========================================================
# TAB 1 - OVERVIEW
# =========================================================
with tab1:

    st.header("Overall Profitability Overview")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:

        # Monthly analysis
        monthly_analysis = (
            filtered_df
            .assign(Month=filtered_df["Order Date"].dt.to_period("M"))
            .groupby("Month")
            .agg(
                Sales=("Sales", "sum"),
                Gross_Profit=("Gross Profit", "sum"),
                Cost=("Cost", "sum")
            )
            .reset_index()
        )

        monthly_analysis["Gross Margin(%)"] = np.where(
            monthly_analysis["Sales"] != 0,
            monthly_analysis["Gross_Profit"]
            / monthly_analysis["Sales"] * 100,
            0
        )

        monthly_analysis["Month"] = (
            monthly_analysis["Month"].astype(str)
        )

        # Sales and profit trend
        fig1, ax1 = plt.subplots(figsize=(10, 5))

        ax1.plot(
            monthly_analysis["Month"],
            monthly_analysis["Sales"],
            marker="o",
            label="Sales"
        )

        ax1.plot(
            monthly_analysis["Month"],
            monthly_analysis["Gross_Profit"],
            marker="o",
            label="Gross Profit"
        )

        ax1.set_title("Monthly Sales vs Gross Profit")
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Amount ($)")
        ax1.tick_params(axis="x", rotation=45)
        ax1.legend()

        plt.tight_layout()

        st.pyplot(fig1)
        plt.close(fig1)


        # Monthly margin trend
        fig2, ax2 = plt.subplots(figsize=(10, 5))

        ax2.plot(
            monthly_analysis["Month"],
            monthly_analysis["Gross Margin(%)"],
            marker="o"
        )

        ax2.axhline(
            margin_threshold,
            linestyle="--",
            label=f"Threshold = {margin_threshold:.0f}%"
        )

        ax2.set_title("Monthly Gross Margin Trend")
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Gross Margin (%)")
        ax2.tick_params(axis="x", rotation=45)
        ax2.legend()

        plt.tight_layout()

        st.pyplot(fig2)
        plt.close(fig2)


        margin_volatility = monthly_analysis[
            "Gross Margin(%)"
        ].std()

        st.info(
            f"Monthly Gross Margin Volatility (standard deviation): "
            f"{margin_volatility:.2f} percentage points"
        )


# =========================================================
# TAB 2 - PRODUCT ANALYSIS
# =========================================================
with tab2:

    st.header("Product Profitability Analysis")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:

        product_analysis = (
            filtered_df
            .groupby(["Product ID", "Product Name"])
            .agg(
                Sales=("Sales", "sum"),
                Units=("Units", "sum"),
                Gross_Profit=("Gross Profit", "sum"),
                Cost=("Cost", "sum")
            )
            .reset_index()
        )

        product_analysis["Gross Margin(%)"] = np.where(
            product_analysis["Sales"] != 0,
            product_analysis["Gross_Profit"]
            / product_analysis["Sales"] * 100,
            0
        )

        product_analysis["Profit per Unit"] = np.where(
            product_analysis["Units"] != 0,
            product_analysis["Gross_Profit"]
            / product_analysis["Units"],
            0
        )

        total_product_sales = product_analysis["Sales"].sum()
        total_product_profit = product_analysis["Gross_Profit"].sum()

        product_analysis["Revenue Contribution (%)"] = np.where(
            total_product_sales != 0,
            product_analysis["Sales"]
            / total_product_sales * 100,
            0
        )

        product_analysis["Profit Contribution (%)"] = np.where(
            total_product_profit != 0,
            product_analysis["Gross_Profit"]
            / total_product_profit * 100,
            0
        )


        # Product classification
        sales_median = product_analysis["Sales"].median()
        margin_median = product_analysis["Gross Margin(%)"].median()

        product_analysis["Performance Category"] = np.select(
            [
                (product_analysis["Sales"] >= sales_median)
                & (product_analysis["Gross Margin(%)"] >= margin_median),

                (product_analysis["Sales"] >= sales_median)
                & (product_analysis["Gross Margin(%)"] < margin_median),

                (product_analysis["Sales"] < sales_median)
                & (product_analysis["Gross Margin(%)"] >= margin_median),

                (product_analysis["Sales"] < sales_median)
                & (product_analysis["Gross Margin(%)"] < margin_median)
            ],
            [
                "High Sales - High Margin",
                "High Sales - Low Margin",
                "Low Sales - High Margin",
                "Low Sales - Low Margin"
            ],
            default="Normal"
        )


        # Filter by margin threshold
        displayed_products = product_analysis[
            product_analysis["Gross Margin(%)"] >= margin_threshold
        ].copy()


        st.write(
            f"Products meeting the selected margin threshold: "
            f"**{len(displayed_products)}**"
        )


        # Product table
        product_display = displayed_products.copy()

        product_display["Sales"] = product_display["Sales"].round(2)
        product_display["Gross_Profit"] = (
            product_display["Gross_Profit"].round(2)
        )
        product_display["Cost"] = product_display["Cost"].round(2)
        product_display["Gross Margin(%)"] = (
            product_display["Gross Margin(%)"].round(2)
        )
        product_display["Profit per Unit"] = (
            product_display["Profit per Unit"].round(2)
        )


        st.dataframe(
            product_display.sort_values(
                "Gross_Profit",
                ascending=False
            ),
            use_container_width=True
        )


        # Top products by profit
        top_products = (
            product_analysis
            .sort_values("Gross_Profit", ascending=False)
            .head(10)
        )

        fig3, ax3 = plt.subplots(figsize=(10, 6))

        sns.barplot(
            data=top_products,
            x="Gross_Profit",
            y="Product Name",
            ax=ax3
        )

        ax3.set_title("Top Products by Gross Profit")
        ax3.set_xlabel("Gross Profit ($)")
        ax3.set_ylabel("Product")

        plt.tight_layout()

        st.pyplot(fig3)
        plt.close(fig3)


        # Sales vs Margin scatter
        fig4, ax4 = plt.subplots(figsize=(10, 6))

        sns.scatterplot(
            data=product_analysis,
            x="Sales",
            y="Gross Margin(%)",
            size="Gross_Profit",
            hue="Performance Category",
            sizes=(80, 600),
            ax=ax4
        )

        ax4.set_title("Product Sales vs Gross Margin")
        ax4.set_xlabel("Sales ($)")
        ax4.set_ylabel("Gross Margin (%)")

        plt.tight_layout()

        st.pyplot(fig4)
        plt.close(fig4)


# =========================================================
# TAB 3 - DIVISION ANALYSIS
# =========================================================
with tab3:

    st.header("Division Performance Analysis")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:

        division_analysis = (
            filtered_df
            .groupby("Division")
            .agg(
                Sales=("Sales", "sum"),
                Cost=("Cost", "sum"),
                Gross_Profit=("Gross Profit", "sum"),
                Units=("Units", "sum")
            )
            .reset_index()
        )

        division_analysis["Gross Margin(%)"] = np.where(
            division_analysis["Sales"] != 0,
            division_analysis["Gross_Profit"]
            / division_analysis["Sales"] * 100,
            0
        )

        division_analysis["Profit per Unit"] = np.where(
            division_analysis["Units"] != 0,
            division_analysis["Gross_Profit"]
            / division_analysis["Units"],
            0
        )


        st.dataframe(
            division_analysis.round(2),
            use_container_width=True
        )


        # Division sales vs profit
        division_melted = division_analysis.melt(
            id_vars="Division",
            value_vars=["Sales", "Gross_Profit"],
            var_name="Metric",
            value_name="Amount"
        )

        fig5, ax5 = plt.subplots(figsize=(10, 5))

        sns.barplot(
            data=division_melted,
            x="Division",
            y="Amount",
            hue="Metric",
            ax=ax5
        )

        ax5.set_title("Division Sales vs Gross Profit")
        ax5.set_xlabel("Division")
        ax5.set_ylabel("Amount ($)")

        plt.tight_layout()

        st.pyplot(fig5)
        plt.close(fig5)


        # Division margin
        fig6, ax6 = plt.subplots(figsize=(8, 5))

        sns.barplot(
            data=division_analysis,
            x="Division",
            y="Gross Margin(%)",
            ax=ax6
        )

        ax6.axhline(
            margin_threshold,
            linestyle="--",
            label=f"Threshold = {margin_threshold:.0f}%"
        )

        ax6.set_title("Division Gross Margin")
        ax6.set_ylabel("Gross Margin (%)")
        ax6.legend()

        plt.tight_layout()

        st.pyplot(fig6)
        plt.close(fig6)


# =========================================================
# TAB 4 - RISK ANALYSIS
# =========================================================
with tab4:

    st.header("Cost & Margin Risk Diagnostics")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:

        product_risk = (
            filtered_df
            .groupby(["Product ID", "Product Name"])
            .agg(
                Sales=("Sales", "sum"),
                Cost=("Cost", "sum"),
                Gross_Profit=("Gross Profit", "sum"),
                Units=("Units", "sum")
            )
            .reset_index()
        )

        product_risk["Gross Margin(%)"] = np.where(
            product_risk["Sales"] != 0,
            product_risk["Gross_Profit"]
            / product_risk["Sales"] * 100,
            0
        )

        product_risk["Profit per Unit"] = np.where(
            product_risk["Units"] != 0,
            product_risk["Gross_Profit"]
            / product_risk["Units"],
            0
        )


        cost_median = product_risk["Cost"].median()
        margin_median = product_risk["Gross Margin(%)"].median()
        sales_median = product_risk["Sales"].median()
        profit_median = product_risk["Gross_Profit"].median()


        product_risk["Risk Flag"] = np.select(
            [
                (product_risk["Sales"] >= sales_median)
                & (product_risk["Gross Margin(%)"] < margin_median),

                (product_risk["Cost"] >= cost_median)
                & (product_risk["Gross Margin(%)"] < margin_median),

                (product_risk["Sales"] < sales_median)
                & (product_risk["Gross_Profit"] < profit_median)
            ],
            [
                "High Sales - Low Margin",
                "High Cost - Low Margin",
                "Low Sales - Low Profit"
            ],
            default="Normal"
        )


        risk_products = product_risk[
            product_risk["Risk Flag"] != "Normal"
        ].copy()


        st.subheader("Risk-Flagged Products")

        if risk_products.empty:
            st.success("No products were flagged under the current filters.")
        else:
            st.dataframe(
                risk_products[
                    [
                        "Product ID",
                        "Product Name",
                        "Sales",
                        "Cost",
                        "Gross_Profit",
                        "Gross Margin(%)",
                        "Profit per Unit",
                        "Risk Flag"
                    ]
                ].round(2),
                use_container_width=True
            )


        # Cost vs margin scatter
        st.subheader("Cost vs Gross Margin")

        fig7, ax7 = plt.subplots(figsize=(10, 6))

        sns.scatterplot(
            data=product_risk,
            x="Cost",
            y="Gross Margin(%)",
            size="Sales",
            hue="Risk Flag",
            sizes=(80, 600),
            ax=ax7
        )

        ax7.axhline(
            margin_median,
            linestyle="--",
            label=f"Median Margin = {margin_median:.2f}%"
        )

        ax7.set_title("Cost vs Gross Margin by Product")
        ax7.set_xlabel("Cost ($)")
        ax7.set_ylabel("Gross Margin (%)")
        ax7.legend(
            bbox_to_anchor=(1.02, 1),
            loc="upper left"
        )

        plt.tight_layout()

        st.pyplot(fig7)
        plt.close(fig7)


        # Cost-to-sales ratio
        product_risk["Cost to Sales Ratio (%)"] = np.where(
            product_risk["Sales"] != 0,
            product_risk["Cost"]
            / product_risk["Sales"] * 100,
            0
        )

        st.subheader("Cost-Heavy Products")

        cost_heavy = (
            product_risk
            .sort_values(
                "Cost to Sales Ratio (%)",
                ascending=False
            )
            .head(10)
        )

        st.dataframe(
            cost_heavy[
                [
                    "Product Name",
                    "Sales",
                    "Cost",
                    "Cost to Sales Ratio (%)",
                    "Gross Margin(%)"
                ]
            ].round(2),
            use_container_width=True
        )


# =========================================================
# TAB 5 - PARETO ANALYSIS
# =========================================================
with tab5:

    st.header("Pareto Contribution Analysis")

    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
    else:

        pareto = (
            filtered_df
            .groupby("Product Name")
            .agg(
                Sales=("Sales", "sum"),
                Gross_Profit=("Gross Profit", "sum")
            )
            .reset_index()
        )


        # Revenue Pareto
        pareto_revenue = pareto.sort_values(
            "Sales",
            ascending=False
        ).reset_index(drop=True)

        total_sales_p = pareto_revenue["Sales"].sum()

        pareto_revenue["Cumulative Revenue (%)"] = np.where(
            total_sales_p != 0,
            pareto_revenue["Sales"].cumsum()
            / total_sales_p * 100,
            0
        )

        revenue_80_count = (
            pareto_revenue["Cumulative Revenue (%)"] <= 80
        ).sum() + 1


        st.subheader("Revenue Contribution")

        fig8, ax8 = plt.subplots(figsize=(11, 6))

        ax8.bar(
            pareto_revenue["Product Name"],
            pareto_revenue["Sales"]
        )

        ax8.set_ylabel("Sales ($)")
        ax8.set_xlabel("Product")
        ax8.set_title("Pareto Analysis - Revenue Contribution")
        ax8.tick_params(axis="x", rotation=75)

        ax8_twin = ax8.twinx()

        ax8_twin.plot(
            pareto_revenue["Product Name"],
            pareto_revenue["Cumulative Revenue (%)"],
            marker="o"
        )

        ax8_twin.axhline(
            80,
            linestyle="--",
            label="80% Revenue"
        )

        ax8_twin.set_ylabel("Cumulative Revenue (%)")

        plt.tight_layout()

        st.pyplot(fig8)
        plt.close(fig8)


        st.info(
            f"Approximately {revenue_80_count} product(s) account for "
            f"the first 80% of cumulative revenue under the current filters."
        )


        # Profit Pareto
        pareto_profit = pareto.sort_values(
            "Gross_Profit",
            ascending=False
        ).reset_index(drop=True)

        total_profit_p = pareto_profit["Gross_Profit"].sum()

        pareto_profit["Cumulative Profit (%)"] = np.where(
            total_profit_p != 0,
            pareto_profit["Gross_Profit"].cumsum()
            / total_profit_p * 100,
            0
        )

        profit_80_count = (
            pareto_profit["Cumulative Profit (%)"] <= 80
        ).sum() + 1


        st.subheader("Profit Contribution")

        fig9, ax9 = plt.subplots(figsize=(11, 6))

        ax9.bar(
            pareto_profit["Product Name"],
            pareto_profit["Gross_Profit"]
        )

        ax9.set_ylabel("Gross Profit ($)")
        ax9.set_xlabel("Product")
        ax9.set_title("Pareto Analysis - Profit Contribution")
        ax9.tick_params(axis="x", rotation=75)

        ax9_twin = ax9.twinx()

        ax9_twin.plot(
            pareto_profit["Product Name"],
            pareto_profit["Cumulative Profit (%)"],
            marker="o"
        )

        ax9_twin.axhline(
            80,
            linestyle="--",
            label="80% Profit"
        )

        ax9_twin.set_ylabel("Cumulative Profit (%)")

        plt.tight_layout()

        st.pyplot(fig9)
        plt.close(fig9)


        st.info(
            f"Approximately {profit_80_count} product(s) account for "
            f"the first 80% of cumulative gross profit under the current filters."
        )


# ---------------------------------------------------------
# KEY BUSINESS INSIGHTS
# ---------------------------------------------------------
st.divider()

st.header("💡 Key Business Insights")

if not filtered_df.empty:

    product_summary = (
        filtered_df
        .groupby("Product Name")
        .agg(
            Sales=("Sales", "sum"),
            Gross_Profit=("Gross Profit", "sum"),
            Cost=("Cost", "sum")
        )
        .reset_index()
    )

    product_summary["Gross Margin(%)"] = np.where(
        product_summary["Sales"] != 0,
        product_summary["Gross_Profit"]
        / product_summary["Sales"] * 100,
        0
    )


    highest_profit_product = (
        product_summary
        .sort_values("Gross_Profit", ascending=False)
        .iloc[0]
    )

    highest_margin_product = (
        product_summary
        .sort_values("Gross Margin(%)", ascending=False)
        .iloc[0]
    )

    lowest_margin_product = (
        product_summary
        .sort_values("Gross Margin(%)", ascending=True)
        .iloc[0]
    )


    insight1, insight2, insight3 = st.columns(3)

    with insight1:
        st.metric(
            "Highest Gross Profit Product",
            highest_profit_product["Product Name"]
        )
        st.write(
            f"Gross Profit: "
            f"${highest_profit_product['Gross_Profit']:,.2f}"
        )

    with insight2:
        st.metric(
            "Highest Margin Product",
            highest_margin_product["Product Name"]
        )
        st.write(
            f"Gross Margin: "
            f"{highest_margin_product['Gross Margin(%)']:.2f}%"
        )

    with insight3:
        st.metric(
            "Lowest Margin Product",
            lowest_margin_product["Product Name"]
        )
        st.write(
            f"Gross Margin: "
            f"{lowest_margin_product['Gross Margin(%)']:.2f}%"
        )


    st.write(
        "### Business Interpretation"
    )

    st.write(
        "The dashboard helps identify products that generate strong gross "
        "profit, products with strong sales but weaker margins, and "
        "products that may require pricing, sourcing, or portfolio review."
    )

    st.write(
        "Cost diagnostics highlight products where relatively high cost "
        "levels are associated with lower gross margins, supporting "
        "potential cost-control and pricing decisions."
    )

    st.write(
        "Pareto analysis helps assess whether revenue or profit is highly "
        "dependent on a relatively small number of products."
    )

else:
    st.warning("No records available for generating business insights.")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()

st.caption(
    "Nassau Candy Distributor | Product Line Profitability & Margin "
    "Performance Analysis | Python • Pandas • Streamlit • Seaborn"
)
