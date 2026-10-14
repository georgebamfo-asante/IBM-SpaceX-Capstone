import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

spacex_df = pd.read_csv("/home/project/spacex_launch_dash.csv")
app = dash.Dash(__name__)

sites = spacex_df["Launch Site"].unique().tolist()
options = [{"label": "All Sites", "value": "ALL"}]
options += [{"label": site, "value": site} for site in sites]

app.layout = html.Div([
    html.H1("SpaceX Launch Records Dashboard"),
    html.Label("Select Launch Site:"),
    dcc.Dropdown(
        id="site-dropdown",
        options=options,
        value="ALL",
        searchable=True
    ),
    dcc.Graph(id="success-pie-chart"),
    html.Label("Payload Range (Kg):"),
    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=10000,
        step=1000,
        value=[0, 10000],
        marks={i: str(i) for i in range(0, 10001, 1000)}
    ),
    dcc.Graph(id="success-payload-scatter-chart")
])

@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value")
)
def get_pie_chart(entered_site):
    filtered = spacex_df if entered_site == "ALL" else spacex_df[
        spacex_df["Launch Site"] == entered_site
    ]
    counts = (
        filtered.groupby("class").size()
        .reset_index(name="Launch Count")
    )
    counts["Outcome"] = counts["class"].map({0: "Failure", 1: "Success"})
    return px.pie(
        counts,
        names="Outcome",
        values="Launch Count",
        title="Launch Success Counts"
    )

@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value")
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered = spacex_df[
        spacex_df["Payload Mass (kg)"].between(low, high)
    ]
    if entered_site != "ALL":
        filtered = filtered[filtered["Launch Site"] == entered_site]
    return px.scatter(
        filtered,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        title="Launch Success vs Payload Mass",
        hover_data=["Launch Site"]
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
