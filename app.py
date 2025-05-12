# -*- coding: utf-8 -*-
"""
Created on Mon May 12 09:34:19 2025

@author: pprajapati
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

app = dash.Dash(__name__)
server = app.server  # Required for Render hosting

# Simulate sensor data
def generate_sensor_data(n=50):
    now = datetime.now()
    time_series = [now - timedelta(seconds=5 * i) for i in range(n)][::-1]
    df = pd.DataFrame({
        'Time': time_series,
        'Temperature': np.random.normal(25, 1, n),
        'Humidity': np.random.normal(60, 5, n),
        'Pressure': np.random.normal(1013, 2, n),
        'Light': np.random.normal(300, 20, n)
    })
    return df

# App layout
app.layout = html.Div([
    html.H2("Real-Time Sensor Data Monitoring (2x2 Grid)", style={'textAlign': 'center'}),

    dcc.Graph(id='sensor-graph'),

    dcc.Interval(
        id='interval-component',
        interval=5000,  # Update every 5 seconds
        n_intervals=0
    )
])

@app.callback(
    Output('sensor-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n):
    df = generate_sensor_data()

    fig = make_subplots(rows=2, cols=2, subplot_titles=('Temperature', 'Humidity', 'Pressure', 'Light'))

    fig.add_trace(go.Scatter(x=df['Time'], y=df['Temperature'], mode='lines+markers'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Humidity'], mode='lines+markers'), row=1, col=2)
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Pressure'], mode='lines+markers'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Light'], mode='lines+markers'), row=2, col=2)

    fig.update_layout(height=600, title_text="Sensor Data (Updated every 5 seconds)")
    return fig

if __name__ == '__main__':
    app.run(debug=True)
