import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Weather Analytics Dashboard", layout="wide")

st.title("Weather Analytics Platform")
st.markdown("---")

def run_query(query):
    with sqlite3.connect("weather_db.db") as conn:
        return pd.read_sql_query(query, conn)

st.sidebar.header("Dashboard Controls")
db_view = st.sidebar.selectbox("Choose View", ["Overview & Analytics", "Raw Relational Tables"])

if db_view == "Overview & Analytics":
    col_heat, col_cold = st.columns(2)
    
    with col_heat:
        with st.container(border=True):
            st.subheader("Extreme Heat Incidents")
            st.caption("Days recording peak temperatures exceeding 40.0°C")
            q_heat = """
            SELECT c.city_name AS 'Location', COUNT(*) AS 'Extreme Heat Days'
            FROM weather_records w
            JOIN cities c ON w.city_id = c.city_id
            WHERE w.temp_max > 40.0
            GROUP BY c.city_name;
            """
            st.dataframe(run_query(q_heat), width="stretch", hide_index=True)
        
    with col_cold:
        with st.container(border=True):
            st.subheader("Extreme Cold Incidents")
            st.caption("Days recording minimum temperatures below 5.0°C")
            q_cold = """
            SELECT c.city_name AS 'Location', COUNT(*) AS 'Extreme Cold Days'
            FROM weather_records w
            JOIN cities c ON w.city_id = c.city_id
            WHERE w.temp_min < 5.0
            GROUP BY c.city_name;
            """
            st.dataframe(run_query(q_cold), width="stretch", hide_index=True)

    st.markdown("---")
    
    with st.container(border=True):
        st.subheader("Precipitation Matrix")
        q2 = """
        SELECT c.city_name, strftime('%m', w.record_date) AS month, SUM(w.precipitation) AS total_precipitation
        FROM weather_records w
        JOIN cities c ON w.city_id = c.city_id
        GROUP BY c.city_name, month;
        """
        precip_data = run_query(q2)
        pivot_df = precip_data.pivot(index='month', columns='city_name', values='total_precipitation').fillna(0)
    
        st.line_chart(
            pivot_df, 
            height=250,
            x_label="Month",
            y_label="mm of Precipitation",
        )

    with st.container(border=True):
        st.subheader("Peak Wind Velocity Records")
        st.caption("Top 10 historical cites and their weeks demonstrating intense air velocity patterns")
        q3 = """
        SELECT 
            c.city_name AS 'City', 
            strftime('%W', w.record_date) AS 'Week No.', 
            ROUND(AVG(w.max_wind_speed), 2) AS 'Avg Wind Speed (km/h)'
        FROM weather_records w
        JOIN cities c ON w.city_id = c.city_id
        GROUP BY c.city_name, [Week No.]
        ORDER BY [Avg Wind Speed (km/h)] DESC
        LIMIT 10;
        """
        st.table(run_query(q3))

else:
    st.header("Normalized Database Inspection")
    
    st.subheader("Cities Table")
    st.dataframe(run_query("SELECT * FROM cities;"), width="stretch")
    
    st.subheader("Weather Records Table (First 100 Rows)")
    st.dataframe(run_query("SELECT * FROM weather_records LIMIT 100;"), width="stretch")