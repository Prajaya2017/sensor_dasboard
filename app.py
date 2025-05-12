# -*- coding: utf-8 -*-
"""
Created on Mon May 12 13:45:25 2025
@author: pprajapati
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd

# Load and preprocess the data
data = pd.read_csv(
    'C:/Campbellsci/LoggerNet/Irgason_garden_Flux_AmeriFluxFormat.dat',
    skiprows=[0, 2, 3],
    header=0
)
data['datetime'] = pd.to_datetime(data['TIMESTAMP'])

# Define variables to plot, reserving one slot for TA sensors combined
variables_to_plot = [
    'FC', 'LE', 'H', 'ET',
    'TAU', 'USTAR',
    'RH_1_1_1', 'PA', 'WS', 'WD', 'VPD',
    'NETRAD', 'SW_IN', 'LW_IN', 'G',
    'TA_COMBINED'  # Placeholder for subplot with TA_1_1_1/2/3
]

# Dash app setup
app = dash.Dash(__name__)
server = app.server

# Layout
app.layout = html.Div([
    html.H2("Sensor Dashboard - 4x4 Subplot View", style={'textAlign': 'center'}),
    dcc.Graph(id='sensor-subplot'),
    dcc.Interval(id='update', interval=60000, n_intervals=0)
])

@app.callback(
    Output('sensor-subplot', 'figure'),
    [Input('update', 'n_intervals')]
)
def update_graph(n):
    fig = make_subplots(rows=4, cols=4, subplot_titles=[
        var if var != 'TA_COMBINED' else 'Air Temperature Sensors (1_1_1, 1_1_2, 1_1_3)'
        for var in variables_to_plot
    ])

    for i, var in enumerate(variables_to_plot):
        row = i // 4 + 1
        col = i % 4 + 1

        if var == 'TA_COMBINED':
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data['TA_1_1_1'], mode='lines', name='TA_1_1_1'
            ), row=row, col=col)
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data['TA_1_1_2'], mode='lines', name='TA_1_1_2'
            ), row=row, col=col)
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data['TA_1_1_3'], mode='lines', name='TA_1_1_3'
            ), row=row, col=col)
        else:
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[var], mode='lines', name=var
            ), row=row, col=col)

    fig.update_layout(height=900, title="16 Sensor Variables", showlegend=True)
    return fig

if __name__ == '__main__':
    app.run(debug=True)
