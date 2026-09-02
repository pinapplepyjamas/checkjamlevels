import pandas as pd
import streamlit as st

st.set_page_config(page_title="RSH Judgements Tracker", layout="wide")
st.title("🏘️ RSH Regulatory Judgements")

try:
  df = pd.read_csv("data.csv")
  search = st.text_input("🔍 Search Landlord or Reg Code")

  col1, col2, col3 = st.columns(3)
  with col1:
    c_filter = st.multiselect(
        "Consumer Grade", options=sorted(df["Consumer grade"].unique())
    )
  with col2:
    g_filter = st.multiselect(
        "Governance Grade", options=sorted(df["Governance Grade"].unique())
    )
  with col3:
    v_filter = st.multiselect(
        "Viability Grade", options=sorted(df["Viability Grade"].unique())
    )

  filtered = df.copy()
  if search:
    filtered = filtered[
        filtered["Landlord"].str.contains(search, case=False, na=False)
        | filtered["Reg Code"].str.contains(search, case=False, na=False)
    ]
  if c_filter:
    filtered = filtered[filtered["Consumer grade"].isin(c_filter)]
  if g_filter:
    filtered = filtered[filtered["Governance Grade"].isin(g_filter)]
  if v_filter:
    filtered = filtered[filtered["Viability Grade"].isin(v_filter)]

  st.metric("Providers Displayed", len(filtered))
  st.dataframe(filtered, use_container_width=True, hide_index=True)
except FileNotFoundError:
  st.info(
      "No snapshot data available yet. Run the tracker once to populate"
      " records."
  )
