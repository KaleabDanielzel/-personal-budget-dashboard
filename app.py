import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- Setup ---
st.set_page_config(page_title="Personal Budget Dashboard", layout="centered")
st.title("💰 Personal Budget Dashboard")

# --- Data ---
def load_data():
    try:
        df = pd.read_csv("expenses.csv", parse_dates=["Date"])
        # Ensure Date column is datetime type
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df.dropna(subset=["Date"], inplace=True)  # Drop rows with invalid dates if any
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Category", "Amount"])

df = load_data()

# --- Input ---
st.header("➕ Add New Expense")
with st.form("expense_form"):
    date = st.date_input("Date", value=datetime.today())
    category = st.selectbox("Category", ["Food", "Rent", "Transport", "Utilities", "Entertainment", "Other"])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add Expense")

    if submitted:
        new_entry = pd.DataFrame([[pd.to_datetime(date), category, amount]], columns=["Date", "Category", "Amount"])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv("expenses.csv", index=False)
        st.success("Expense added!")

# --- Dashboard ---
if not df.empty:
    st.header("📊 Expense Overview")

    # Monthly total: create a proper datetime column for grouping by month
    df["Month_Year"] = df["Date"].dt.to_period("M").dt.to_timestamp()

    monthly_total = df.groupby("Month_Year")["Amount"].sum().reset_index()

    st.subheader("Monthly Spending")
    monthly_total = monthly_total.sort_values("Month_Year")
    monthly_total.index = monthly_total["Month_Year"].dt.strftime("%B %Y")
    st.bar_chart(monthly_total["Amount"])

    # Category breakdown
    st.subheader("Spending by Category")
    category_total = df.groupby("Category")["Amount"].sum().reset_index()
    fig = px.pie(category_total, values="Amount", names="Category", title="Category Breakdown")
    st.plotly_chart(fig)

    # Raw data
    with st.expander("📄 Show Raw Data"):
        st.dataframe(df.sort_values("Date", ascending=False))

else:
    st.info("No expenses yet. Add your first one above!")
