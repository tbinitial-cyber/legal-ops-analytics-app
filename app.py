import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import os
from auth import authenticate

st.set_page_config(page_title="Legal Operations Analytics Platform", layout="wide")

# ------------------------------------------------
# HEADER
# ------------------------------------------------

st.title("⚖️ Legal Operations Analytics Platform")
st.caption("Operational Intelligence for Legal Departments")

# ------------------------------------------------
# AUDIT LOGGING
# ------------------------------------------------

def log_action(user, action):

    log = pd.DataFrame([{
        "timestamp": datetime.datetime.now(),
        "user": user,
        "action": action
    }])

    os.makedirs("logs", exist_ok=True)

    try:
        log.to_csv("logs/audit_log.csv", mode="a", header=False, index=False)
    except:
        log.to_csv("logs/audit_log.csv", index=False)

# ------------------------------------------------
# DATASET VALIDATION
# ------------------------------------------------

required_files = [
    "data/matter_master_dataset.csv",
    "data/legal_spend_dataset.csv",
    "data/legal_workflow_dataset.csv",
    "data/litigation_dataset.csv"
]

for file in required_files:
    if not os.path.exists(file):
        st.error("Dataset files missing. Run dataset_generator.py first.")
        st.stop()

# ------------------------------------------------
# CACHED DATA LOADING
# ------------------------------------------------

@st.cache_data
def load_data():

    matter = pd.read_csv("data/matter_master_dataset.csv")
    spend = pd.read_csv("data/legal_spend_dataset.csv")
    workflow = pd.read_csv("data/legal_workflow_dataset.csv")
    litigation = pd.read_csv("data/litigation_dataset.csv")

    return matter, spend, workflow, litigation

matter, spend, workflow, litigation = load_data()

# ------------------------------------------------
# INSIGHT ENGINE
# ------------------------------------------------

def generate_insights(spend, workflow, matter):

    insights = []

    if len(spend) > 0:

        top_firm = (
            spend.groupby("law_firm")["approved_invoice_amount"]
            .sum()
            .sort_values(ascending=False)
            .idxmax()
        )

        insights.append(f"Top legal spend is with **{top_firm}**.")

    if len(workflow) > 0:

        sla_rate = workflow["sla_met"].mean()

        if sla_rate < 0.8:
            insights.append("⚠️ SLA compliance below 80%. Process improvement recommended.")
        else:
            insights.append("✅ SLA performance is strong.")

    if len(matter) > 0:

        high_complex = (
            matter["matter_complexity"].value_counts().idxmax()
        )

        insights.append(f"Most matters are **{high_complex} complexity**.")

    return insights

# ------------------------------------------------
# LOGIN
# ------------------------------------------------

if "role" not in st.session_state:

    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        role = authenticate(username, password)

        if role:

            st.session_state["role"] = role
            st.session_state["user"] = username

            log_action(username, "Login")

            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid credentials")

    st.stop()

role = st.session_state["role"]
user = st.session_state["user"]

# ------------------------------------------------
# SIDEBAR FILTERS
# ------------------------------------------------

st.sidebar.title("Filters")

region_filter = st.sidebar.multiselect(
    "Region",
    matter["region"].unique(),
    default=list(matter["region"].unique())
)

practice_filter = st.sidebar.multiselect(
    "Practice Area",
    matter["practice_area"].unique(),
    default=list(matter["practice_area"].unique())
)

filtered_matters = matter[
    (matter["region"].isin(region_filter)) &
    (matter["practice_area"].isin(practice_filter))
]

valid_ids = filtered_matters["matter_id"]

spend = spend[spend["matter_id"].isin(valid_ids)]
workflow = workflow[workflow["matter_id"].isin(valid_ids)]
litigation = litigation[litigation["matter_id"].isin(valid_ids)]

# ------------------------------------------------
# NAVIGATION
# ------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.selectbox(
    "Select Page",
    ["Overview", "Legal Spend", "Workflow Efficiency", "Litigation Risk"]
)

st.sidebar.markdown("---")
st.sidebar.write(f"Logged in as: **{user}**")
st.sidebar.write(f"Role: **{role}**")

# ------------------------------------------------
# OVERVIEW
# ------------------------------------------------

if page == "Overview":

    log_action(user, "Viewed Overview")

    st.header("Legal Department Overview")

    gross_spend = spend["invoice_amount"].sum()
    net_spend = spend["approved_invoice_amount"].sum()
    savings = spend["savings"].sum()

    avg_review = workflow["review_time_days"].mean()
    sla_rate = workflow["sla_met"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Gross Legal Spend", f"${gross_spend:,.0f}")
    col2.metric("Net Spend", f"${net_spend:,.0f}")
    col3.metric("Savings Generated", f"${savings:,.0f}")
    col4.metric("SLA Compliance", f"{sla_rate*100:.1f}%")

    st.subheader("AI Insight Panel")

    insights = generate_insights(spend, workflow, filtered_matters)

    for i in insights:
        st.info(i)

# ------------------------------------------------
# LEGAL SPEND
# ------------------------------------------------

if page == "Legal Spend":

    if role in ["admin","legal_ops"]:

        log_action(user, "Viewed Legal Spend")

        st.header("Legal Spend Analysis")

        spend_by_firm = (
            spend.groupby("law_firm")["approved_invoice_amount"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            spend_by_firm,
            x="law_firm",
            y="approved_invoice_amount",
            title="Spend by Law Firm"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Matter Drill Down")

        firm = st.selectbox(
            "Select Law Firm",
            spend["law_firm"].unique()
        )

        firm_matters = spend[spend["law_firm"] == firm]

        drill = firm_matters.merge(
            filtered_matters,
            on="matter_id"
        )

        st.dataframe(drill)

        csv = drill.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download Report",
            csv,
            "legal_spend_report.csv",
            "text/csv"
        )

    else:
        st.warning("Access restricted.")

# ------------------------------------------------
# WORKFLOW
# ------------------------------------------------

if page == "Workflow Efficiency":

    if role in ["admin","legal_ops"]:

        log_action(user, "Viewed Workflow")

        st.header("Legal Workflow Efficiency")

        avg_time = workflow["review_time_days"].mean()
        sla_rate = workflow["sla_met"].mean()

        col1, col2 = st.columns(2)

        col1.metric("Average Review Time", f"{avg_time:.2f} days")
        col2.metric("SLA Compliance Rate", f"{sla_rate*100:.1f}%")

        req = workflow["request_type"].value_counts().reset_index()
        req.columns = ["request_type","count"]

        fig = px.bar(req, x="request_type", y="count")

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Access restricted.")

# ------------------------------------------------
# LITIGATION
# ------------------------------------------------

if page == "Litigation Risk":

    if role == "admin":

        log_action(user, "Viewed Litigation")

        st.header("Litigation Risk Overview")

        outcome = litigation["case_outcome"].value_counts().reset_index()
        outcome.columns = ["case_outcome","count"]

        fig = px.pie(outcome, names="case_outcome", values="count")

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Restricted to admin users.")