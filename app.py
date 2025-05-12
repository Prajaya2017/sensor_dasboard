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

# App layout with Tabs
app.layout = html.Div([
    html.H2("Real-Time Sensor Data Monitoring (2x2 Grid)", style={'textAlign': 'center'}),
    
    dcc.Tabs(id="tabs", children=[
        # First Tab with 2x2 Grid Plots
        dcc.Tab(label='Sensor Data Tab 1', children=[
            html.Div([
                dcc.Graph(id='sensor-graph-1'),

                dcc.Interval(
                    id='interval-component-1',
                    interval=5000,  # Update every 5 seconds
                    n_intervals=0
                )
            ])
        ]),

        # Second Tab with 2x2 Grid Plots
        dcc.Tab(label='Sensor Data Tab 2', children=[
            html.Div([
                dcc.Graph(id='sensor-graph-2'),

                dcc.Interval(
                    id='interval-component-2',
                    interval=5000,  # Update every 5 seconds
                    n_intervals=0
                )
            ])
        ])
    ])
])

# Callback to update Graph 1
@app.callback(
    Output('sensor-graph-1', 'figure'),
    Input('interval-component-1', 'n_intervals')
)
def update_graph_1(n):
    df = generate_sensor_data()

    fig = make_subplots(rows=2, cols=2, subplot_titles=('Temperature', 'Humidity', 'Pressure', 'Light'))

    fig.add_trace(go.Scatter(x=df['Time'], y=df['Temperature'], mode='lines+markers'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Humidity'], mode='lines+markers'), row=1, col=2)
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Pressure'], mode='lines+markers'), row=2, col=1)
    fig.add_trace(go.Scatter(x=df['Time'], y=df['Light'], mode='lines+markers'), row=2, col=2)

    fig.update_layout(height=600, title_text="Sensor Data (Updated every 5 seconds)")
    return fig

# Callback to update Graph 2 (same function, just tied to another tab)
@app.callback(
    Output('sensor-graph-2', 'figure'),
    Input('interval-component-2', 'n_intervals')
)
def update_graph_2(n):
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
