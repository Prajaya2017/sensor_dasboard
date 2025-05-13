import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Load and preprocess data
data = pd.read_csv('Irgason_garden_Flux_AmeriFluxFormat.dat',
                   skiprows=[0, 2, 3], header=0)
data['datetime'] = pd.to_datetime(data['TIMESTAMP'])

# Replace outlier G values
data['G'] = data['G'].where((data['G'] <= 900) & (data['G'] >= -900), np.nan)

# Variables for each tab
tab1_variables = [
    'FC', 'LE', 'H', 'ET',
    'TAU', 'USTAR',
    'RH_1_1_1', 'PA', 'WS', 'WD', 'VPD',
    'TA_COMBINED', 'SWC_1_1_1', 'SWC_1_1_2', 'SWC_1_1_3', 'PBLH'
]

tab2_variables = [
    'CO2', 'H2O', 'FETCH_MAX', 'FETCH_90',
    'FETCH_40', 'ZL', 'MO_LENGTH', 'U_SIGMA',
    'V_SIGMA', 'W_SIGMA', 'P', 'T_SONIC',
    'SWC', 'U-V-W SIGMA', 'USTAR vs WS', 'VPD'
]

# Tab style matching U-V-W Sigma color
tab_style = {
    'padding': '8px',
    'fontWeight': 'bold',
    'backgroundColor': '#eaf2fb',
    'border': '1px solid #1f77b4',
    'borderRadius': '3px',
    'margin': '5px',
    'color': '#1f77b4'
}
selected_tab_style = {
    **tab_style,
    'backgroundColor': '#1f77b4',
    'color': 'white'
}

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Flux and Met Variables", style={'textAlign': 'center'}),
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='Var I', value='tab1', style=tab_style, selected_style=selected_tab_style),
        dcc.Tab(label='Var II', value='tab2', style=tab_style, selected_style=selected_tab_style),
    ]),
    html.Div(id='tab-content'),
    dcc.Interval(id='update', interval=60000, n_intervals=0)
])

@app.callback(
    Output('tab-content', 'children'),
    Input('tabs', 'value'),
    Input('update', 'n_intervals')
)
def update_graph(tab, n):
    if tab == 'tab1':
        fig = make_subplots(rows=4, cols=4, subplot_titles=[
            var if var != 'TA_COMBINED' else 'TA'
            for var in tab1_variables
        ],                             
        horizontal_spacing=0.03,
        vertical_spacing=0.06)

        for i, var in enumerate(tab1_variables):
            row, col = i // 4 + 1, i % 4 + 1
            if var == 'TA_COMBINED':
                for sensor in ['TA_1_1_1', 'TA_1_1_2', 'TA_1_1_3']:
                    fig.add_trace(go.Scatter(
                        x=data['datetime'], y=data[sensor], mode='lines', name=sensor,
                        line=dict(width=1)
                    ), row=row, col=col)
            else:
                fig.add_trace(go.Scatter(
                    x=data['datetime'], y=data[var], mode='lines', name=var,
                    line=dict(width=1)
                ), row=row, col=col)

        # Set font size for subplot titles
        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(size=12)

        fig.update_layout(
            height=900,
            showlegend=False,
            font=dict(size=10),
            margin=dict(t=40, b=40, l=40, r=40),
        )

        fig.update_xaxes(tickangle=25, tickformat="%m-%d-%y")

        return dcc.Graph(figure=fig)

    elif tab == 'tab2':
        fig = make_subplots(rows=4, cols=4, subplot_titles=[
            'CO2', 'H2O', 'FETCH_MAX', 'FETCH_90',
            'FETCH_40', 'ZL', 'MO_LENGTH', 'U_SIGMA',
            'NET RADIOMETER', 'V_SIGMA', 'W_SIGMA', 'P',
            'T_SONIC', 'SWC', 'USTAR vs WS', 'VPD'
        ],
        horizontal_spacing=0.03, vertical_spacing=0.06)

        vars_to_plot = [
            'CO2', 'H2O', 'FETCH_MAX', 'FETCH_90',
            'FETCH_40', 'ZL', 'MO_LENGTH', 'U_SIGMA',
            'V_SIGMA', 'W_SIGMA', 'P', 'T_SONIC'
        ]

        for i, var in enumerate(vars_to_plot):
            row, col = i // 4 + 1, i % 4 + 1
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[var], mode='lines', name=var,
                line=dict(width=1)
            ), row=row, col=col)

        # Net Radiometer (subplot 9)
        fig.add_trace(go.Scatter(x=data['datetime'], y=data['NETRAD'], mode='lines', name='NETRAD', line=dict(width=1)), row=3, col=1)
        fig.add_trace(go.Scatter(x=data['datetime'], y=data['SW_IN'], mode='lines', name='SW_IN', line=dict(width=1)), row=3, col=1)
        fig.add_trace(go.Scatter(x=data['datetime'], y=data['SW_OUT'], mode='lines', name='SW_OUT', line=dict(width=1)), row=3, col=1)
        fig.add_trace(go.Scatter(x=data['datetime'], y=data['LW_IN'], mode='lines', name='LW_IN', line=dict(width=1)), row=3, col=1)
        fig.add_trace(go.Scatter(x=data['datetime'], y=data['LW_OUT'], mode='lines', name='LW_OUT', line=dict(width=1)), row=3, col=1)

        # SWC group (subplot 14)
        fig.add_trace(go.Scatter(x=data['datetime'], y=data['SWC_1_1_1'], mode='lines', name='SWC_1_1_1', line=dict(width=1)), row=4, col=2)
        fig.add_trace(go.Scatter(x=data['datetime'], y=data['SWC_1_1_2'], mode='lines', name='SWC_1_1_2', line=dict(width=1)), row=4, col=2)
        fig.add_trace(go.Scatter(x=data['datetime'], y=data['SWC_1_1_3'], mode='lines', name='SWC_1_1_3', line=dict(width=1)), row=4, col=2)

        # Scatter USTAR vs WS (subplot 15)
        fig.add_trace(go.Scatter(x=data['USTAR'], y=data['WS'], mode='markers', name='USTAR vs WS', marker=dict(size=4, opacity=0.6)), row=4, col=3)

        # VPD (subplot 16)
        fig.add_trace(go.Scatter(x=data['datetime'], y=data['VPD'], mode='lines', name='VPD', line=dict(width=1)), row=4, col=4)

        # Set font size for subplot titles
        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(size=12)

        fig.update_layout(
            height=1200,
            showlegend=False,
            font=dict(size=10),
            margin=dict(t=30, b=30, l=30, r=30),
            title_font_size=10
        )

        fig.update_xaxes(tickangle=25, tickformat="%m-%d-%y")

        return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run(debug=True)
