
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Sales Explorer", layout="wide")

@st.cache_data
def make_data(n_rows=5000, seed=42):
    rng = np.random.default_rng(seed)
    # Synthetic taxonomy
    countries = ["United States", "United Kingdom", "Germany", "France", "India", "United Arab Emirates", "Singapore", "Australia", "Brazil", "Canada"]
    cities_by_country = {
        "United States": ["New York", "San Francisco", "Austin", "Chicago", "Seattle"],
        "United Kingdom": ["London", "Manchester", "Birmingham", "Leeds"],
        "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt"],
        "France": ["Paris", "Lyon", "Marseille", "Toulouse"],
        "India": ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai"],
        "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah"],
        "Singapore": ["Singapore"],
        "Australia": ["Sydney", "Melbourne", "Brisbane"],
        "Brazil": ["São Paulo", "Rio de Janeiro", "Brasília"],
        "Canada": ["Toronto", "Vancouver", "Montreal"]
    }
    segments = ["Consumer", "Corporate", "Small Business", "Enterprise"]
    products = ["Laptop", "Phone", "Tablet", "Monitor", "Headphones", "Printer", "Router", "Keyboard", "Mouse", "Camera"]

    start = pd.Timestamp("2023-01-01")
    end = pd.Timestamp("2025-08-01")
    dates = pd.to_datetime(rng.integers(start.value//10**9, end.value//10**9, size=n_rows), unit="s")

    country = rng.choice(countries, size=n_rows, p=np.array([0.12,0.07,0.07,0.06,0.18,0.12,0.06,0.08,0.12,0.12]))
    city = np.array([rng.choice(cities_by_country[c]) for c in country])
    segment = rng.choice(segments, size=n_rows, p=[0.45,0.25,0.2,0.1])
    product = rng.choice(products, size=n_rows)

    # Customers: generate per country-segment buckets to make it realistic
    cust_ids = []
    cust_names = []
    for i in range(n_rows):
        base = f"{country[i][:2].upper()}{segment[i][:2].upper()}"
        cid = base + f"{rng.integers(1000,9999)}"
        cust_ids.append(cid)
        cust_names.append(f"Customer {cid}")

    units = rng.integers(1, 10, size=n_rows)
    unit_price = rng.uniform(30, 2500, size=n_rows).round(2)

    # Add discount noise and margin structure by segment
    seg_margin = {"Consumer": 0.18, "Corporate": 0.22, "Small Business": 0.15, "Enterprise": 0.28}
    discount = rng.choice([0, 0.05, 0.1, 0.15], size=n_rows, p=[0.55,0.25,0.15,0.05])
    gross_sales = units * unit_price
    net_sales = gross_sales * (1 - discount)
    profit = np.array([ns * seg_margin[s] * rng.uniform(0.8, 1.2) for ns, s in zip(net_sales, segment)])

    df = pd.DataFrame({
        "OrderDate": dates.normalize(),
        "OrderID": rng.integers(1_000_000, 9_999_999, size=n_rows),
        "Country": country,
        "City": city,
        "Segment": segment,
        "CustomerID": cust_ids,
        "CustomerName": cust_names,
        "Product": product,
        "Units": units,
        "UnitPrice": unit_price,
        "Discount": discount,
        "Sales": net_sales.round(2),
        "Profit": profit.round(2),
    })
    df.sort_values("OrderDate", inplace=True)
    return df

df = make_data()

st.title("📈 Sales Explorer — Country, Customer, Location, Segment")

# --------------- Sidebar Filters ---------------
st.sidebar.header("Filters")
min_date, max_date = df["OrderDate"].min(), df["OrderDate"].max()
date_range = st.sidebar.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)

countries = st.sidebar.multiselect("Country", sorted(df["Country"].unique()))
segments = st.sidebar.multiselect("Segment", sorted(df["Segment"].unique()))

# Dependently restrict city and customer choices based on earlier picks
df_stage = df.copy()
if len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    df_stage = df_stage[(df_stage["OrderDate"] >= start) & (df_stage["OrderDate"] <= end)]

if countries:
    df_stage = df_stage[df_stage["Country"].isin(countries)]
if segments:
    df_stage = df_stage[df_stage["Segment"].isin(segments)]

cities = st.sidebar.multiselect("City", sorted(df_stage["City"].unique()))
if cities:
    df_stage = df_stage[df_stage["City"].isin(cities)]

customers = st.sidebar.multiselect("Customer", sorted(df_stage["CustomerName"].unique()))
if customers:
    df_stage = df_stage[df_stage["CustomerName"].isin(customers)]

st.sidebar.caption("Tip: Start broad, then narrow down to cities or customers.")

# --------------- KPIs ---------------
total_sales = df_stage["Sales"].sum()
total_profit = df_stage["Profit"].sum()
orders = df_stage["OrderID"].nunique()
aov = df_stage.groupby("OrderID")["Sales"].sum().mean() if orders > 0 else 0.0

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"${total_sales:,.0f}")
k2.metric("Total Profit", f"${total_profit:,.0f}")
k3.metric("Orders", f"{orders:,}")
k4.metric("Avg Order Value", f"${aov:,.0f}")

st.divider()

# --------------- Charts ---------------
c1, c2 = st.columns((2,1))

# Sales over time
sales_daily = df_stage.groupby("OrderDate", as_index=False)["Sales"].sum()
fig_time = px.line(sales_daily, x="OrderDate", y="Sales", title="Sales Over Time")
c1.plotly_chart(fig_time, use_container_width=True)

# Sales by country
country_sales = df_stage.groupby("Country", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
fig_country = px.bar(country_sales, x="Country", y="Sales", title="Sales by Country")
c2.plotly_chart(fig_country, use_container_width=True)

# Sales by segment
seg_sales = df_stage.groupby("Segment", as_index=False)[["Sales","Profit"]].sum()
fig_seg = px.bar(seg_sales, x="Segment", y=["Sales","Profit"], barmode="group", title="Sales & Profit by Segment")
st.plotly_chart(fig_seg, use_container_width=True)

# Top customers
top_customers = df_stage.groupby("CustomerName", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False).head(15)
fig_cust = px.bar(top_customers, x="Sales", y="CustomerName", orientation="h", title="Top 15 Customers by Sales")
st.plotly_chart(fig_cust, use_container_width=True)

# Product mix
prod_sales = df_stage.groupby("Product", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False).head(10)
fig_prod = px.pie(prod_sales, names="Product", values="Sales", title="Top Product Mix (by Sales)")
st.plotly_chart(fig_prod, use_container_width=True)

# Profitability scatter
sample = df_stage.sample(n=min(3000, len(df_stage)), random_state=7) if len(df_stage) > 0 else df_stage
fig_scatter = px.scatter(sample, x="Sales", y="Profit", color="Segment", hover_data=["Country","City","CustomerName","Product"], title="Order Profit vs Sales")
st.plotly_chart(fig_scatter, use_container_width=True)

# Raw data
with st.expander("Show raw data"):
    st.dataframe(df_stage, use_container_width=True)

st.caption("Data is synthetic and generated on the fly for demo purposes. Adjust the code in make_data() to mirror your real-world distribution.")
