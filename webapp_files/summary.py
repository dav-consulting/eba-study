import streamlit as st


def summary_stats(state):
    st.title(":chart_with_upwards_trend: Dashboard page")
    st.write("Slider state:", state.slider)
