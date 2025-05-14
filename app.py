# -*- coding: utf-8 -*-
"""
Created on Tue May 13 19:54:19 2025

@author: pprajapati
"""

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
# force numeric conversion (invalid parsing becomes NaN)
data['G'] = pd.to_numeric(data['G'], errors='coerce')

# now apply the range filter
data['G'] = data['G'].where((data['G'] <= 900) & (data['G'] >= -500), np.nan)


# Variables for each tab
tab1_variables = [
    'FC', 'LE', 'H', 'ET',
    'TAU', 'USTAR',
    'RH_1_1_1', 'PA', 'WS', 'WD', 'VPD',
    'TA_COMBINED', 'PBLH'
]

tab2_variables = [
     'CO2', 'H2O', 'FETCH_MAX', 'FETCH_90',
    'FETCH_40', 'ZL', 'MO_LENGTH', 'P', 'T_SONIC','NET RAD'
    'SWC', 'U-V-W SIGMA', 'USTAR vs WS'
]

# Styles
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
        ], horizontal_spacing=0.03, vertical_spacing=0.06)

        for i, var in enumerate(tab1_variables):
            row, col = i // 4 + 1, i % 4 + 1
            if var == 'TA_COMBINED':
                for j, sensor in enumerate(['TA_1_1_1', 'TA_1_1_2', 'TA_1_1_3']):
                    fig.add_trace(go.Scatter(
                        x=data['datetime'], y=data[sensor], mode='lines', name=sensor,
                        line=dict(width=1),
                        showlegend=(j == 0),
                        legendgroup='TA',
                        legendgrouptitle_text='TA Sensors',
                        hovertemplate='%{x|%Y-%m-%d %H:%M:%S}<br>' + sensor + ': %{y:.2f}<extra></extra>'
                    ), row=row, col=col)
            else:
                fig.add_trace(go.Scatter(
                    x=data['datetime'], y=data[var], mode='lines', name=var,
                    line=dict(width=1),
                    hovertemplate='%{x|%Y-%m-%d %H:%M:%S}<br>' + var + ': %{y:.2f}<extra></extra>'
                ), row=row, col=col)

        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(size=12)

        fig.update_layout(
            height=1200,
            showlegend=False,
            hovermode='x unified',
            font=dict(size=10),
            margin=dict(t=40, b=40, l=40, r=40),
        )

        fig.update_xaxes(tickangle=25, tickformat="%m-%d-%y")

        return dcc.Graph(figure=fig)

    elif tab == 'tab2':
        fig = make_subplots(rows=4, cols=4, subplot_titles=[
            'CO2', 'H2O', 'FETCH_MAX', 'FETCH_90',
            'FETCH_40', 'ZL', 'MO_LENGTH', 'P', 'T_SONIC',
            'NET RAD','SWC', 'U-V-W SIGMA', 'USTAR vs WS'
        ], horizontal_spacing=0.03, vertical_spacing=0.06)

        vars_to_plot = [
             'CO2', 'H2O', 'FETCH_MAX', 'FETCH_90',
            'FETCH_40', 'ZL', 'MO_LENGTH', 'P', 'T_SONIC'
        ]

        for i, var in enumerate(vars_to_plot):
            row, col = i // 4 + 1, i % 4 + 1
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[var], mode='lines', name=var,
                line=dict(width=1),
                hovertemplate='%{x|%Y-%m-%d %H:%M:%S}<br>' + var + ': %{y:.2f}<extra></extra>'
            ), row=row, col=col)
            
        rad_cols = ['NETRAD', 'SW_IN', 'SW_OUT', 'LW_IN', 'LW_OUT']
        for col in rad_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce')
            data[col] = data[col].clip(lower=-200, upper=2000)

        # Net Radiation group
        for j, var in enumerate(rad_cols):
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[var], mode='lines', name=var,
                showlegend=(j == 0),
                legendgroup='NetRad',
                legendgrouptitle_text='Net Radiation',
                line=dict(width=1),
                hovertemplate='%{x|%Y-%m-%d %H:%M:%S}<br>' + var + ': %{y:.2f}<extra></extra>'
            ), row=3, col=2)



        swc_cols = ['SWC_1_1_1', 'SWC_1_1_2', 'SWC_1_1_3']
        for col in swc_cols:
            data[col] = pd.to_numeric(data[col], errors='coerce')  # convert invalid entries to NaN
            data[col] = data[col].clip(lower=-900, upper=900)  # soil water content typically between 0 and 1

        # SWC group (subplot 14)
        for j, swc in enumerate(swc_cols):
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[swc], mode='lines', name=swc,
                showlegend=(j == 0),
                legendgroup='SWC',
                legendgrouptitle_text='SWC Sensors',
                line=dict(width=1),
                hovertemplate='%{x|%Y-%m-%d %H:%M:%S}<br>' + swc + ': %{y:.2f}<extra></extra>'
            ), row=3, col=3)


            
            
        for j, swc in enumerate(['U_SIGMA','V_SIGMA', 'W_SIGMA']):
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[swc], mode='lines', name=swc,
                showlegend=(j == 0),
                legendgroup='UVW',
                legendgrouptitle_text='U_V_W_SIGMA',
                line=dict(width=1),
                hovertemplate='%{x|%Y-%m-%d %H:%M:%S}<br>' + swc + ': %{y:.2f}<extra></extra>'
            ), row=3, col=4)


        # Drop NA values for USTAR and WS
        reg_data = data[['USTAR', 'WS']].dropna()

        # Linear regression
        x = reg_data['USTAR']
        y = reg_data['WS']
        slope, intercept = np.polyfit(x, y, 1)
        r_value = np.corrcoef(x, y)[0, 1]
        r_squared = r_value**2

        # Regression line
        x_line = np.linspace(x.min(), x.max(), 100)
        y_line = slope * x_line + intercept

        # Scatter points
        fig.add_trace(go.Scatter(
            x=x, y=y, mode='markers', name='USTAR vs WS',
            marker=dict(size=4, opacity=0.6, color='rgba(0, 100, 200, 0.5)'),
            hovertemplate='USTAR: %{x:.2f}<br>WS: %{y:.2f}<extra></extra>'
        ), row=4, col=1)

        # Regression line
        fig.add_trace(go.Scatter(
            x=x_line, y=y_line, mode='lines', name='Regression Line',
            line=dict(color='firebrick', width=2, dash='dash'),
            hoverinfo='skip'
        ), row=4, col=1)

        # Add regression equation and R² as annotation
        fig.add_annotation(
            xref='x domain', yref='y domain',
            x=0.05, y=0.95,
            text=f'y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.2f}',
            showarrow=False,
            font=dict(size=11, color='black'),
            align='left',
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1,
            row=4, col=1
        )


       
        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(size=12)

        fig.update_layout(
            height=1200,
            showlegend=False,
            hovermode='x unified',
            font=dict(size=10),
            margin=dict(t=30, b=30, l=30, r=30),
        )

        fig.update_xaxes(tickangle=25, tickformat="%m-%d-%y")

        return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run(debug=True)