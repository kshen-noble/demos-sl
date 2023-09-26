import streamlit as st
import pandas as pd
import plotly.express as px


df = pd.read_csv("v4_chevron.csv",index_col=False)


# ===== Display
st.markdown("# Chevron literature review")

# Histogram
st.markdown("# A Figure")

types = ["H2","O2","CO"]  #df["yield_1"].unique()

for type in types:
    tmp = df[ df["yield_1"]==type ]
    st.markdown(f"### Yield of type {type}")
    fig = px.box(tmp,"yield_1_amt",points="all",hover_data=["yield_1","yield_1_units","doi"]) #,"noble_filename_abbrev","article_title"])
    fig.update_layout(showlegend=False)
    fig.update_layout(
        width=800,
        height=400,
)
    st.plotly_chart(fig, use_container_width=True)


