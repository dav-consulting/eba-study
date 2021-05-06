import pandas as pd
import numpy as np
import plotly as py
import plotly.graph_objs as go

colors = [
    "#FBB802",
    "#B71150",
    "#039997",
    "#014088",
    "#FD3500",
    "#7A10D8",
    "#34eb34",
    "#3474eb",
    "#b734eb",
    "#eb34c9",
]
config = {"displayModeBar": False}


class Dav_vizualisation:
    def __init__(self, data):
        self.data = data

    ## * Function for visulizing pie graph with one single serie
    def dav_pie(self, series=str(), head_title=str()):
        holder = self.data[series]
        holder.dropna(inplace=True)
        n = len(holder)  # .dropna())
        data = pd.value_counts(holder.values, sort=True)
        labels = holder.value_counts().index.tolist()
        trace = go.Pie(
            labels=labels,
            values=data,
            textfont=dict(size=10),
            hole=0.65,
            marker=dict(colors=colors, line=dict(color="#000000", width=0.5)),
            title="n: {}".format(n),
        )
        layout = go.Layout(
            title=head_title, font=dict(size=10), autosize=False, width=600, height=400
        )
        fig = go.Figure(data=[trace], layout=layout)
        return fig

    ## * Function for visulizing bar graph with one series

    def dav_bar(self, series=str(), head_title=str(), show_percent=True):
        holder = self.data[series]
        holder.dropna(inplace=True)
        data = pd.value_counts(holder.values, sort=True, normalize=show_percent)
        labels = holder.value_counts().index.tolist()
        trace = go.Bar(
            x=labels,
            y=data,
            name=series,
            width=0.6,
            marker=dict(color=colors, line=dict(color="#000000", width=0.5)),
            text=data.values,
            textposition="inside",
        )
        layout = go.Layout(
            barmode="group",
            title=head_title,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            width=600,
            height=400,
            font=dict(size=10),
            # yaxis={"tickformat": ",.0%", "range": [0, 1]},
        )
        fig = go.Figure(data=[trace], layout=layout,)
        return fig

    ## * Function for visulizing bar graph with one serie for stacked layout
    def dav_bars_stacked(
        self, grouped_serie=str(), data_serie=str(), head_title=str(),
    ):
        holder_group = self.data.groupby(grouped_serie)
        trace_list = []
        for grp, data_ in holder_group:
            trace = go.Bar(
                x=data_[data_serie].value_counts().index,
                y=data_[data_serie].value_counts(),
                name=grp,
                width=0.6,
                marker=dict(line=dict(color="black", width=0.5)),
                text=data_[data_serie].value_counts().values,
                textposition="inside",
            )
            trace_list.append(trace)
        layout = go.Layout(
            barmode="stack",
            title=head_title,
            font=dict(size=10),
            autosize=True,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            width=600,
            height=400,
            yaxis=dict(showgrid=True, gridcolor="rgb(245, 245, 245)"),
        )
        fig = go.Figure(data=trace_list, layout=layout,)
        # fig.update_xaxes(title_text=grouped_serie)
        return fig

