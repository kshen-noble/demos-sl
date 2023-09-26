import streamlit as st
import pandas as pd
import plotly.express as px


df = pd.read_csv("chemical_only_and_E.csv",index_col=False)


# ===== Display
st.markdown("# Title")
st.write("#### Extra comments")


# Histogram
st.markdown("# A Figure")
st.markdown("#### More comments")
fig = px.box(df,"output_E",points="all",hover_data=["input_Ui","input_NCO/OH PP"])
fig.update_layout(showlegend=False)
fig.update_layout(
    width=800,
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

