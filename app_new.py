# app.py

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# Load and preprocess data
url = "https://raw.githubusercontent.com/Prajaya2017/sensor_dasboard/main/Irgason_garden_AmrFlux.dat"
data = pd.read_csv(url, skiprows=[0, 2, 3], header=0)

exclude_cols = ['TIMESTAMP', 'TIMESTAMP_START', 'TIMESTAMP_END']
cols_to_convert = [col for col in data.columns if col not in exclude_cols]
data[cols_to_convert] = data[cols_to_convert].apply(pd.to_numeric, errors='coerce')
data['datetime'] = pd.to_datetime(data['TIMESTAMP'], errors='coerce')
data = data.drop_duplicates(subset='datetime', keep='first')

# Reindex to ensure time continuity (1-hour frequency)
data = data.set_index('datetime')
full_index = pd.date_range(start=data.index.min(), end=data.index.max(), freq='h')
data = data.reindex(full_index)
data.index.name = 'datetime'
data.reset_index(inplace=True)

# Filter invalid ranges
#data['G'] = data['G'].where((data['G'] <= 900) & (data['G'] >= -500), np.nan)

tab1_variables = ['FC', 'LE', 'H', 'TAU', 'USTAR', 'RH_1_1_3', 'PA', 'WS', 'WD', 'VPD', 'TA_COMBINED']
tab2_variables = ['CO2', 'H2O', 'FETCH_MAX', 'FETCH_90', 'zL', 'MO_LENGTH', 'P', 'T_SONIC', 'NET RAD', 'SWC', 'U-V-W SIGMA', 'USTAR vs WS']

tab_style = {'padding': '8px', 'fontWeight': 'bold', 'backgroundColor': '#eaf2fb', 'border': '1px solid #1f77b4', 'borderRadius': '3px', 'margin': '5px', 'color': '#1f77b4'}
selected_tab_style = {**tab_style, 'backgroundColor': '#1f77b4', 'color': 'white'}

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H2("Real Time Data Monitor - Instrument Garden", style={'textAlign': 'center'}),
    dcc.Tabs(id='tabs', value='tab1', children=[
        dcc.Tab(label='FLUX MET VAR I', value='tab1', style=tab_style, selected_style=selected_tab_style),
        dcc.Tab(label='FLUX MET VAR II', value='tab2', style=tab_style, selected_style=selected_tab_style),
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
            'CO₂ Flux (µmol m⁻² s⁻¹)', 'Latent Heat Flux (W m⁻²)', 'Sensible Heat Flux (W m⁻²)',
            'Momentum Flux (kg m⁻¹ s⁻²)', 'Friction Velocity (m s⁻¹)', 'Relative Humidity (%)', 'Atmospheric Pressure (kPa)',
            'Wind Speed (m s⁻¹)', 'Wind Direction (°)', 'Vapor Pressure Deficit (kPa)', 'Air Temperature (°C)'], horizontal_spacing=0.03, vertical_spacing=0.06)

        for i, var in enumerate(tab1_variables):
            row, col = i // 4 + 1, i % 4 + 1
            if var == 'TA_COMBINED':
                TA_cols = ['TA_1_1_1', 'TA_1_1_2', 'TA_1_1_3']
                for col_name in TA_cols:
                    data[col_name] = data[col_name].clip(lower=-20, upper=45)
                    fig.add_trace(go.Scatter(
                        x=data['datetime'], y=data[col_name], mode='lines', name=col_name,
                        line=dict(width=1), connectgaps=False,
                        showlegend=(col_name == 'TA_1_1_1'),
                        legendgroup='TA', legendgrouptitle_text='TA Sensors',
                        hovertemplate='%{x|%Y-%m-%d %H:%M}<br>' + col_name + ': %{y:.2f}<extra></extra>'
                    ), row=row, col=col)
            else:
                fig.add_trace(go.Scatter(
                    x=data['datetime'], y=data[var], mode='lines', name=var,
                    line=dict(width=1), connectgaps=False,
                    hovertemplate='%{x|%Y-%m-%d %H:%M}<br>' + var + ': %{y:.2f}<extra></extra>'
                ), row=row, col=col)

        fig.update_layout(height=1200, showlegend=False, hovermode='x unified', font=dict(size=10),
                          margin=dict(t=40, b=40, l=40, r=40))
        fig.update_xaxes(tickangle=25, tickformat="%m-%d-%y")
        return dcc.Graph(figure=fig)

    elif tab == 'tab2':
        fig = make_subplots(rows=4, cols=4, subplot_titles=[
            'CO₂ Concentration (ppm)', 'H₂O Concentration (mmol mol⁻¹)', 'Max Fetch (m)', '90% Fetch (m)',
            'Soil Heat Flux (W m⁻²)', 'Stability Parameter (z/L)', 'Monin-Obukhov Length (m)', 'Precipitation (mm)',
            'Sonic Temp (°C)', 'Net Radiation (W m⁻²)', 'Soil Water Content (m³ m⁻³)', 'σ (m s⁻¹)', 'USTAR vs WS'
        ], horizontal_spacing=0.03, vertical_spacing=0.06)

        vars_to_plot = ['CO2', 'H2O', 'FETCH_MAX', 'FETCH_90', 'zL', 'MO_LENGTH', 'P', 'T_SONIC']
        for i, var in enumerate(vars_to_plot):
            row, col = i // 4 + 1, i % 4 + 1
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[var], mode='lines', name=var,
                line=dict(width=1), connectgaps=False,
                hovertemplate='%{x|%Y-%m-%d %H:%M}<br>' + var + ': %{y:.2f}<extra></extra>'
            ), row=row, col=col)

        rad_cols = ['NETRAD', 'SW_IN', 'SW_OUT', 'LW_IN', 'LW_OUT']
        for col in rad_cols:
            data[col] = data[col].clip(lower=-200, upper=2000)
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[col], mode='lines', name=col,
                showlegend=(col == 'NETRAD'), legendgroup='NetRad', legendgrouptitle_text='Net Radiation',
                line=dict(width=1), connectgaps=False,
                hovertemplate='%{x|%Y-%m-%d %H:%M}<br>' + col + ': %{y:.2f}<extra></extra>'
            ), row=3, col=2)

        swc_cols = ['SWC_1_1_1', 'SWC_1_1_2', 'SWC_1_1_3']
        for swc in swc_cols:
            data[swc] = data[swc].clip(lower=-900, upper=900)
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[swc], mode='lines', name=swc,
                showlegend=(swc == 'SWC_1_1_1'), legendgroup='SWC', legendgrouptitle_text='SWC Sensors',
                line=dict(width=1), connectgaps=False,
                hovertemplate='%{x|%Y-%m-%d %H:%M}<br>' + swc + ': %{y:.2f}<extra></extra>'
            ), row=3, col=3)

        for i, swc in enumerate(['U_SIGMA', 'V_SIGMA', 'W_SIGMA']):
            fig.add_trace(go.Scatter(
                x=data['datetime'], y=data[swc], mode='lines', name=swc,
                showlegend=(swc == 'U_SIGMA'), legendgroup='UVW', legendgrouptitle_text='U_V_W_SIGMA',
                line=dict(width=1), connectgaps=False,
                hovertemplate='%{x|%Y-%m-%d %H:%M}<br>' + swc + ': %{y:.2f}<extra></extra>'
            ), row=3, col=4)

        reg_data = data[['USTAR', 'WS']].dropna()
        if not reg_data.empty:
            x, y = reg_data['USTAR'], reg_data['WS']
            slope, intercept = np.polyfit(x, y, 1)
            r_squared = np.corrcoef(x, y)[0, 1] ** 2
            x_line = np.linspace(x.min(), x.max(), 100)
            y_line = slope * x_line + intercept
            fig.add_trace(go.Scatter(x=x, y=y, mode='markers', name='USTAR vs WS',
                                     marker=dict(size=4, opacity=0.6, color='rgba(0,100,200,0.5)'),
                                     hovertemplate='USTAR: %{x:.2f}<br>WS: %{y:.2f}<extra></extra>'
                                     ), row=4, col=1)
            fig.add_trace(go.Scatter(x=x_line, y=y_line, mode='lines', name='Regression Line',
                                     line=dict(color='firebrick', width=2, dash='dash'),
                                     hoverinfo='skip'
                                     ), row=4, col=1)
            fig.add_annotation(xref='x domain', yref='y domain', x=0.05, y=0.95,
                               text=f'y = {slope:.2f}x + {intercept:.2f}<br>R² = {r_squared:.2f}',
                               showarrow=False, font=dict(size=11, color='black'), align='left',
                               bgcolor='rgba(255,255,255,0.8)', bordercolor='gray', borderwidth=1,
                               row=4, col=1)

        fig.update_layout(height=1200, showlegend=False, hovermode='x unified',
                          font=dict(size=10), margin=dict(t=30, b=30, l=30, r=30))
        fig.update_xaxes(tickangle=25, tickformat="%m-%d-%y")
        return dcc.Graph(figure=fig)

if __name__ == '__main__':
    app.run(debug=True)