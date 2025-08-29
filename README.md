# Sales Explorer (Streamlit)

An interactive Streamlit app to explore synthetic sales data **country-wise, customer-wise, location-wise (city), and segment-wise**.

## Features
- Reproducible synthetic dataset (no external files needed)
- Sidebar filters: date range, country, segment, city, customer
- KPIs: Total Sales, Total Profit, Orders, Avg Order Value
- Charts: Time series, country bar, segment bar, top customers, product mix, profit vs sales scatter
- Raw data preview

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Community Cloud
1. Push this folder to a GitHub repo (e.g., `sales-explorer-streamlit`).
2. On https://streamlit.io/cloud, create a new app, and select your repo and `app.py` as the entry point.
3. The app generates data at runtime, so no dataset files are required.

## Customize
- Edit `make_data()` in `app.py` to tweak product lists, countries, margins, or volume.
- Replace synthetic generation with a CSV/DB connection and keep the same UI/filters.