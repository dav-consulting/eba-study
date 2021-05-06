# app.py
# https://eba.davcon.mywire.org/
import streamlit as st
from streamlit.hashing import _CodeHasher
import pandas as pd
import numpy as np
import os
import sys
from collections import Counter
from dateutil.parser import parse
from util import db_connect

# from webapp_files import summary, documentation
from webapp_files import dav_viz as dv

## * import data
conn, cur = db_connect()
df = pd.read_sql_query(
    "SELECT * FROM eba_evaluations WHERE series=='Sida Decentralised Evaluation' AND series_number NOT LIKE '2008%' AND series_number NOT LIKE '2009%' AND series_number NOT LIKE '2010%' ;",
    conn,
)
df = df[df.publ_date != "2019­02­04"]  ## remove entry with flawed publ_date

## * filter functions
def single_year(data):
    try:
        result = str(parse(data, fuzzy=True).year)
        return result.strip(".")
    except:
        return np.nan


def convert_q9(data):
    if data == "ja":
        return "Sida sole donor"
    else:
        return "Multidonors"


def convert_q21(data):
    if data == "ja":
        return "Sida mentioned"
    else:
        return "No reference found"


def convert_q22(data):
    if data == "ja":
        return "Donor dependency"
    else:
        return "No reference found"


def convert_commisioned_by(data):
    if "Sida" in data:
        return "Sida"
    elif "Embassy" in data:
        return "Embassy"
    else:
        return "Other"


def convert_q6(data):
    try:
        years = data.split("-")
        result = [int(year) for year in years]
        sum = max(result) - min(result)
        return sum
    except:
        return np.nan


def top_10_countries(data):
    country_evaluations = []
    for c in data["q3"]:
        for countries in c.split(";"):
            country_evaluations.append(countries.strip())
    df = pd.DataFrame.from_dict(
        Counter(country_evaluations), orient="index", columns=["count"]
    ).sort_values(by="count", ascending=False)

    return df.head(20)


## * selection functions
def selected_year(selection, df):
    all_years = (
        str(df.year.dropna().unique().min())
        + "-"
        + str(df.year.dropna().unique().max())
    )

    if selection == "2012-" + str(df.year.dropna().unique().max()):
        return df
    else:
        df_selection = df.loc[df["year"] == selection]
        return df_selection


def selected_geo(selection, df):
    if selection == "All":
        return df
    else:
        df_selection = df.loc[df["q5"] == selection]
        return df_selection


def selected_eval_type(selection, df):
    if selection == "All":
        return df
    else:
        df_selection = df.loc[df["q14"] == selection]
        return df_selection


## * converting data with more informative lables
def return_df(data):
    """Fix data for dashboard with more informative lables"""

    data["year"] = data.publ_date.apply(lambda x: single_year(x))
    data["sole_donor"] = data.q9.apply(lambda x: convert_q9(x))
    data["sida_importance"] = data.q21.apply(lambda x: convert_q21(x))
    data["donor_dependency"] = data.q22.apply(lambda x: convert_q22(x))
    data["commisioned_entity"] = data.commisioned_by.apply(
        lambda x: convert_commisioned_by(x)
    )
    data["evaluation_length"] = data.q6.apply(lambda x: convert_q6(x))

    return data


## * drafting raw dataframe
df_raw = return_df(df)


all_years_drop_val = (
    str(df_raw.year.dropna().unique().min())
    + "-"
    + str(df_raw.year.dropna().unique().max())
)

## * drafting dropdown options
year_options = [all_years_drop_val] + sorted(
    df_raw.year.dropna().unique(), reverse=True
)
geo_options = ["All"] + sorted(df_raw.q5.dropna().unique(), reverse=False)
eval_type_options = ["All"] + sorted(df_raw.q14.dropna().unique(), reverse=False)

## * app layout
st.beta_set_page_config(layout="wide")
st.sidebar.title("Navigation")
year_dropdown = st.sidebar.selectbox("Select year:", year_options,)
geo_dropdown = st.sidebar.selectbox("Select geographical focus:", geo_options)
eval_type_dropdown = st.sidebar.selectbox("Select evaluation type:", eval_type_options)

## * filter df and make instance of dav viz class
df_select = dv.Dav_vizualisation(
    selected_year(
        year_dropdown,
        selected_geo(geo_dropdown, selected_eval_type(eval_type_dropdown, df_raw)),
    )
)

df_select_list = selected_year(
    year_dropdown,
    selected_geo(geo_dropdown, selected_eval_type(eval_type_dropdown, df_raw)),
)


df_url_list = selected_year(
    year_dropdown,
    selected_geo(
        geo_dropdown, selected_eval_type(eval_type_dropdown, df_raw.set_index("title"))
    ),
)


df_all = dv.Dav_vizualisation(df_raw)


st.title(
    "Descriptive statistics of Sida's decentralised evaluations between {} and {}".format(
        str(df_raw.year.dropna().unique().min()),
        str(df_raw.year.dropna().unique().max()),
    )
)
st.write(
    "This page will display estimations derived from the EBA study *Exploring the Potential of Data Science Methods for Systematic Review Automation Within the Field of International Development Cooperation*. The displayed data below is derived from an automated process that currently has collected and analysed {} evaluations".format(
        len(df_raw)
    )
    + ". Note that the depicted numbers are estimations and that the data is likely to have a certain degree of error. Consideration for how to use the data appropriate is therefore adviced."
)


st.plotly_chart(
    df_all.dav_bar(
        "year", "Number of conducted evaluations over time", show_percent=False
    ),
    use_container_width=True,
)

st.plotly_chart(
    df_all.dav_bars_stacked("q5", "year", "Geographic focus over time"),
    use_container_width=True,
)


st.plotly_chart(
    df_all.dav_bars_stacked("q14", "year", "Type of evaluation over time"),
    use_container_width=True,
)


st.markdown("---")

st.header(
    "Descriptive statistics of Sida's decentralised evaluations for {}".format(
        year_dropdown
    )
)


st.markdown(
    "The graphs in this section can be controlled via the interactive navigation panel to the left. The available filter varibles are *individual year, geographical focus, and type of evaluation*. All but the two first graphs will automatically adjust depending on the selction made. Currently the graphs show data for {}".format(
        year_dropdown
    )
)

### FIX ###
### Q23-Q25 NEED TO BE REFACTORED

data = df_select_list[
    [
        "q23",
        "q23_impacts",
        "q23_relevance",
        "q23_effectiveness",
        "q23_efficiency",
        "q24_q25",
        "q24_q25_relevance",
        "q24_q25_impacts",
        "q24_q25_effectiveness",
        "q24_q25_efficiency",
    ]
]

summary_d = {}
rec_d = {}
for c in data:
    val = data[c].value_counts(normalize=True)
    interim = []

    if val.index[0] == "ja":
        # print(val.values[0])
        interim.append(val.values[0])
    else:
        # print(val.values[1])
        interim.append(val.values[1])
    if "q23" in c:
        summary_d[c] = round(interim[0] * 100, 1)
    else:
        rec_d[c] = round(interim[0] * 100, 1)

d = {"In recommendations": rec_d, "In summary": summary_d}
dd = pd.DataFrame(d)
dd.reset_index(inplace=True)
dd["index"].replace(
    {
        "q23": "Sustainability",
        "q23_relevance": "Relevance",
        "q23_impacts": "Impacts",
        "q23_effectiveness": "Effectiveness",
        "q23_efficiency": "Efficiency",
        "q24_q25": "Sustainability",
        "q24_q25_relevance": "Relevance",
        "q24_q25_impacts": "Impacts",
        "q24_q25_effectiveness": "Effectiveness",
        "q24_q25_efficiency": "Efficiency",
    },
    inplace=True,
)
dd.set_index("index", inplace=True)

d1 = dd.drop(columns="In recommendations").dropna()
d2 = dd.drop(columns="In summary").dropna()
df_f = d1.join(d2)

import plotly.graph_objects as go


dac_fig = go.Figure(
    data=[
        go.Bar(
            name=df_f["In summary"].name,
            x=df_f.index,
            y=df_f["In summary"],
            text=df_f["In summary"],
            textposition="auto",
            marker=dict(line=dict(color="black", width=0.5)),
        ),
        go.Bar(
            name=df_f["In recommendations"].name,
            x=df_f.index,
            y=df_f["In recommendations"],
            text=df_f["In recommendations"],
            textposition="auto",
            marker=dict(line=dict(color="black", width=0.5)),
        ),
    ],
)

# Change the bar mode
dac_fig.update_layout(
    barmode="group",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    title="Percent of evaluations with OECD/DAC criteria in Summary and Recommendation for {}".format(
        year_dropdown
    ),
    font=dict(size=10),
    autosize=True,
)
st.plotly_chart(dac_fig)

### FIX ###

col1, col2, = st.beta_columns(2)
with col1:

    st.plotly_chart(
        df_select.dav_pie("q5", "Geographic focus for {}".format(year_dropdown)),
        use_container_width=True,
    )

with col2:
    st.plotly_chart(
        df_select.dav_bars_stacked(
            "q14",
            "q5",
            "Type of evaluation group by geographic focus area for {}".format(
                year_dropdown
            ),
        ),
        use_container_width=True,
    )


col3, col4, = st.beta_columns(2)
with col3:

    st.plotly_chart(
        df_select.dav_bars_stacked(
            "sida_importance",
            "q5",
            "Discussion of Sida's support in realation to sustainability {}".format(
                year_dropdown
            ),
        ),
        use_container_width=True,
    )


with col4:
    st.plotly_chart(
        df_select.dav_pie(
            "commisioned_entity",
            "Commissioning entity of the evaluations for {}".format(year_dropdown),
        ),
        use_container_width=True,
    )

col5, col6, = st.beta_columns(2)
with col5:

    st.plotly_chart(
        df_select.dav_pie(
            "sole_donor", "Estimate for involved donors for {}".format(year_dropdown),
        ),
        use_container_width=True,
    )


with col6:

    st.plotly_chart(
        df_select.dav_bars_stacked(
            "donor_dependency",
            "q5",
            "Donor dependendency is discussed for {}".format(year_dropdown),
        ),
        use_container_width=True,
    )

st.markdown("---")

st.header("Access to processed evaluations at Sida' online publication database")

st.markdown("---")
st.write(
    "This section holds hyperlinks to the processed evaluations that has been selected in the navigation panel to the right. Currently the list holds evaluations for {}".format(
        year_dropdown
    ),
)

df_url_list = df_url_list.reset_index()
df_url_list.web_doc_url = df_url_list.apply(
    lambda x: f'<a href="{x["web_doc_url"]}">{x["title"]}</a>', axis=1
)
df_url_list = df_url_list.rename(
    columns={"web_doc_url": "document link", "series_number": "Series number"},
    inplace=False,
).sort_values("Series number")


st.write(
    df_url_list[["Series number", "document link"]].to_html(escape=False, index=False),
    unsafe_allow_html=True,
)

# st.write("\n")
# st.write("\n")
# st.write("\n")
# st.write(
#    "Top observed countries for the selected time period - {}".format(year_dropdown)
# )
# st.bar_chart(top_10_countries(df_select_list))

