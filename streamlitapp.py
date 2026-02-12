import streamlit as st
import altair as alt
from snowflake.snowpark.context import get_active_session

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

st.title("Superstore Profit Heatmap Explorer")

# Get Snowflake session
session = get_active_session()

@st.cache_data
def load_data():
    query = """
    select category, segment, region, profit, sales, quantity
    from sales_raw
    """
    return session.sql(query).to_pandas()

df = load_data()


st.sidebar.header("Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    df["REGION"].unique(),
    default=df["REGION"].unique()
)

metric = st.sidebar.selectbox(
    "Select Metric",
    ["PROFIT", "SALES", "QUANTITY"]
)

agg_func = st.sidebar.selectbox(
    "Aggregation",
    ["SUM", "AVG"]
)


filtered_df = df[df["REGION"].isin(regions)]

if agg_func == "SUM":
    grouped = filtered_df.groupby(
        ["CATEGORY", "SEGMENT"]
    )[metric].sum().reset_index()
else:
    grouped = filtered_df.groupby(
        ["CATEGORY", "SEGMENT"]
    )[metric].mean().reset_index()


col1, col2, col3 = st.columns(3)

col1.metric("Rows Used", len(filtered_df))
col2.metric("Categories", grouped["CATEGORY"].nunique())
col3.metric("Segments", grouped["SEGMENT"].nunique())

chart = alt.Chart(grouped).mark_rect().encode(
    x=alt.X("SEGMENT:O", title="Segment"),
    y=alt.Y("CATEGORY:O", title="Category"),
    color=alt.Color(f"{metric}:Q", title=metric),
    tooltip=["CATEGORY", "SEGMENT", metric]
).properties(height=400)

st.subheader(f"{agg_func} {metric} Heatmap")

st.altair_chart(chart, use_container_width=True)


if st.checkbox("Show aggregated table"):
    st.dataframe(grouped)

st.download_button(
    "Download Data CSV",
    grouped.to_csv(index=False),
    file_name="heatmap_data.csv"
)