import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output, State
from django_plotly_dash import DjangoDash
from .models import DynamicTableLoader
import datetime
import logging

PAGE_SIZE = 10  # Display 10 rows at a time initially

app = DjangoDash('quote_evolution_dashboard')

# Static options for year and arrondissements
STATIC_YEARS = [2010, 2011, 2012, 2013, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2070]
STATIC_ARRONDISSEMENTS = [10, 11, 12, 21, 22, 23, 24, 25, 31, 32, 33, 34, 35, 41, 42, 43, 44, 45, 46, 51, 52, 53, 54, 0]

# Get the current year
current_year = datetime.datetime.now().year

# Add the current year to the list if it's not already present
if current_year not in STATIC_YEARS:
    STATIC_YEARS.append(current_year)
    STATIC_YEARS.sort()

# Centralized function to load data
def get_dash_data(years=None, arrondissements=None):
    data = []
    columns = []
    try:
        # Convert years and arrondissements to strings if provided
        if years and arrondissements:
            for year in years:
                for arrondissement in arrondissements:
                    cols, rows = DynamicTableLoader.load_data(year, arrondissement)
                    if not columns:
                        columns = cols
                    data.extend(rows)

        df = pd.DataFrame(data, columns=columns)

        # Rename columns according to the Django model field names (if needed)
        df.rename(columns={
            'Numéro ES': 'Num_ES',
            'Catégorie UIC': 'Cat_UIC',
            "Type d'appareil": 'Type_AW',
            'Vitesse branche directe': 'V_directe',
            'Vitesse branche déviée': 'V_déviée',
            'Coeur(s) fissuré(s)': 'Coeur_fissuré',
            'Gare / Bifurcation': 'Gare_Bifurcation',
            'Catégorie de voie': 'Cat_voie',
            'Modèle coeur P1': 'Modèle_P1',
            'Modèle coeur P2': 'Modèle_P2',
            "Nombre d'attaques compl.": 'Nombre_att_compl',
            'Rayon voie directe': 'Rayon_directe',
            'Nominale verkanting': 'Nom_verkanting',
            'Model halve tongenstellen': 'Model_halve_tongenstellen',
            'Modèle coeur K1/K2': 'Modèle_K1_K2',
            'Arrond.': 'Arr',
            'Poste': 'Poste',
            'No. Ident.': 'Ramses_id',
            'Date de contrôle': 'Date_control',
            'Date dernier contrôle': 'Date_last_control',
            'Type de contrôle': 'Type_control',
            'Règle 1': 'Tool_id',
            'Périodicité': 'Périodicité',
            'Fiche remplie par:': 'Author',
            'Date validation SMS': 'Date_validation_SMS'
        }, inplace=True)

        return df

    except Exception as e:
        logging.error(f"Error in get_dash_data: {str(e)}")
        return pd.DataFrame()  # Return an empty DataFrame on error

# Layout for the Dash app
app.layout = html.Div([
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': str(year), 'value': year} for year in STATIC_YEARS],
        multi=True,
        placeholder="Select years"
    ),
    dcc.Dropdown(
        id='arrondissement-dropdown',
        options=[{'label': f'Arrond.: {arr}', 'value': arr} for arr in STATIC_ARRONDISSEMENTS],
        multi=True,
        placeholder="Select arrondissements"
    ),
    html.Button('Load Data', id='load-data-button', n_clicks=0),
    dcc.Dropdown(
        id='ramses-id-dropdown',
        options=[],
        placeholder="Select Ramses ID",
        searchable=True,
        clearable=True
    ),
    dcc.Dropdown(
        id='quote-name-dropdown',
        options=[],
        placeholder="Select Quote Name",
        searchable=True,
        clearable=True
    ),
    dcc.DatePickerRange(
        id='date-picker-range',
        start_date=None,
        end_date=None,
        display_format='DD-MM-YYYY',
        start_date_placeholder_text='DD-MM-YYYY',
        end_date_placeholder_text='DD-MM-YYYY',
        calendar_orientation='horizontal',
        clearable=True,
    ),
    dcc.Graph(id='quote-measured-value-graph'),
    dcc.Graph(id='gauge-chart'),  # Add the gauge chart component here
    html.Div(id='kpi-slope', style={'margin-top': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
    html.Div(id='kpi-last-two-points-slope', style={'margin-top': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
    html.Div(id='latest-kpi-value', style={'margin-top': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
    html.Div(id='latest-kpi-ial-max', style={'margin-top': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
    html.Div(id='latest-kpi-ial-min', style={'margin-top': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
    html.Div(id='latest-kpi-il-max', style={'margin-top': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
    html.Div(id='latest-kpi-il-min', style={'margin-top': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
    html.Div(id='latest-kpi-al-max', style={'margin-top': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
    html.Div(id='latest-kpi-al-min', style={'margin-top': '20px', 'fontSize': '24px', 'fontWeight': 'bold'}),
    html.Div(id='loaded-rows', style={'display': 'none'}, children='0')
],
    className='dash-app-container')

# Callback for Ramses ID dropdown
@app.callback(
    Output('ramses-id-dropdown', 'options'),
    Input('load-data-button', 'n_clicks'),
    State('year-dropdown', 'value'),
    State('arrondissement-dropdown', 'value')
)
def update_ramses_dropdown(n_clicks, selected_years, selected_arrondissements):
    if n_clicks == 0 or not selected_years or not selected_arrondissements:
        return []

    try:
        df = get_dash_data(years=selected_years, arrondissements=selected_arrondissements)
        ramses_id_options = [{'label': str(ramses_id), 'value': str(ramses_id)} for ramses_id in df['Ramses_id'].unique()]
        return ramses_id_options

    except Exception as e:
        logging.error(f"Error in update_ramses_dropdown: {str(e)}")
        return []

# Callback for Quote Name dropdown
@app.callback(
    Output('quote-name-dropdown', 'options'),
    Input('ramses-id-dropdown', 'value'),
    State('year-dropdown', 'value'),
    State('arrondissement-dropdown', 'value')
)
def update_quote_name_dropdown(selected_ramses_id, selected_years, selected_arrondissements):
    if not selected_ramses_id or not selected_years or not selected_arrondissements:
        return []

    try:
        df = get_dash_data(years=selected_years, arrondissements=selected_arrondissements)
        df = df[df['Ramses_id'] == selected_ramses_id]
        quote_name_options = [{'label': str(quote_name), 'value': str(quote_name)} for quote_name in df['Quote_name'].unique()]
        return quote_name_options

    except Exception as e:
        logging.error(f"Error in update_quote_name_dropdown: {str(e)}")
        return []

@app.callback(
    [
        Output('quote-measured-value-graph', 'figure'),
        Output('gauge-chart', 'figure'),  # Output for gauge chart
        Output('kpi-slope', 'children'),
        Output('kpi-last-two-points-slope', 'children'),
        Output('loaded-rows', 'children'),
        Output('latest-kpi-value', 'children'),
        Output('latest-kpi-ial-max', 'children'),
        Output('latest-kpi-ial-min', 'children'),
        Output('latest-kpi-il-max', 'children'),
        Output('latest-kpi-il-min', 'children'),
        Output('latest-kpi-al-max', 'children'),
        Output('latest-kpi-al-min', 'children')
    ],
    [
        Input('quote-name-dropdown', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ],
    [
        State('ramses-id-dropdown', 'value'),
        State('year-dropdown', 'value'),
        State('arrondissement-dropdown', 'value'),
        State('loaded-rows', 'children')
    ]
)
def update_graph(selected_quote_name, start_date, end_date, selected_ramses_id, selected_years, selected_arrondissements, loaded_rows):
    slope = 0.0
    last_two_points_slope = 0.0
    latest_value = None
    latest_ial_max = None
    latest_ial_min = None
    latest_il_max = None
    latest_il_min = None
    latest_al_max = None
    latest_al_min = None

    if not selected_quote_name or not selected_ramses_id or not selected_years or not selected_arrondissements:
        return [go.Figure(), go.Figure(), "No data available", "No data available", loaded_rows, "No data available", "No data available", "No data available", "No data available", "No data available", "No data available", "No data available"]

    try:
        df = get_dash_data(years=selected_years, arrondissements=selected_arrondissements)

        df = df[df['Ramses_id'] == selected_ramses_id]
        df = df[df['Quote_name'] == selected_quote_name]

        if start_date:
            df = df[df['Date_control'] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df['Date_control'] <= pd.to_datetime(end_date)]

        if df.empty:
            logging.warning("The DataFrame is empty after applying filters.")
            return go.Figure(), go.Figure(), "No matching data", "No matching data", loaded_rows, "No matching data", "No matching data", "No matching data", "No matching data", "No matching data", "No matching data"

        df['Quote_measured_value'] = pd.to_numeric(df['Quote_measured_value'], errors='coerce')
        df_filtered = df.dropna(subset=['Quote_measured_value'])

        if not df_filtered.empty:
            df_filtered['Date_control'] = pd.to_datetime(df_filtered['Date_control'], dayfirst=True)
            df_filtered = df_filtered.sort_values(by='Date_control')

            # Get the latest value and IAL_max
            latest_value = df_filtered['Quote_measured_value'].iloc[-1]
            latest_ial_max = df_filtered['IAL_max'].iloc[-1] if not df_filtered['IAL_max'].isna().all() else ""
            latest_ial_min = df_filtered['IAL_min'].iloc[-1] if not df_filtered['IAL_min'].isna().all() else ""
            latest_il_max = df_filtered['IL_max'].iloc[-1] if not df_filtered['IL_max'].isna().all() else ""
            latest_il_min = df_filtered['IL_min'].iloc[-1] if not df_filtered['IL_min'].isna().all() else ""
            latest_al_max = df_filtered['AL_max'].iloc[-1] if not df_filtered['AL_max'].isna().all() else ""
            latest_al_min = df_filtered['AL_min'].iloc[-1] if not df_filtered['AL_min'].isna().all() else ""

            def safe_convert_latest(value):
                if pd.isna(value) or value == "":
                    return 0.0
                return float(value)

            latest_value = df_filtered['Quote_measured_value'].iloc[-1]
            latest_ial_max = safe_convert_latest(df_filtered['IAL_max'].iloc[-1])
            latest_ial_min = safe_convert_latest(df_filtered['IAL_min'].iloc[-1])
            latest_il_max = safe_convert_latest(df_filtered['IL_max'].iloc[-1])
            latest_il_min = safe_convert_latest(df_filtered['IL_min'].iloc[-1])
            latest_al_max = safe_convert_latest(df_filtered['AL_max'].iloc[-1])
            latest_al_min = safe_convert_latest(df_filtered['AL_min'].iloc[-1])

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df_filtered['Date_control'],
                y=df_filtered['Quote_measured_value'],
                mode='lines+markers',
                name='Quote Measured Value',
                line=dict(color='blue')
            ))

            line_colors = {
                'IAL_min': 'rgba(255,0,0,0.5)',  
                'IAL_max': 'rgba(255,0,0,0.5)',  
                'IL_min': 'rgba(255,105,180,0.5)',  
                'IL_max': 'rgba(255,105,180,0.5)',  
                'AL_min': 'rgba(255,165,0,0.5)',  
                'AL_max': 'rgba(255,165,0,0.5)'   
            }

            columns_to_plot = ['IAL_min', 'IAL_max', 'IL_min', 'IL_max', 'AL_min', 'AL_max']
            for col in columns_to_plot:
                if df_filtered[col].ne(0).sum() > 0:
                    fig.add_trace(go.Scatter(
                        x=df_filtered['Date_control'],
                        y=df_filtered[col],
                        mode='lines',
                        name=col,
                        line=dict(color=line_colors[col])
                    ))

            fig.update_layout(
                title=f"AW {selected_ramses_id} quote {selected_quote_name} over time",
                title_x=0.5,
                xaxis_title='',
                yaxis_title='',
                showlegend=True,
                xaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=False, showgrid=False, zeroline=False),
                yaxis=dict(showline=True, linewidth=2, linecolor='black', mirror=False, showgrid=False, zeroline=False),
                plot_bgcolor='white'
            )

            Quote_name_general = df_filtered['Quote_name_general'].iloc[-1]

            Both_ends_gauge = ['E','Ebis', 'CE','Ec', 'X','Tx','T','Ecartement ']
            One_end_lower_gauge = ['A', 'D','F',  'J','L', 'S', 'Dp ()',
            'DwrL', 'DwrR', 'M', 'M_value', 'Z',  'Fbis',
            'Jbis','Z jeu max mm','Ua', 'Uca', 'Ud','s',
            'Jeux aiguilles/coussinets', 'M_value_value', 'Dpl D', 'Dpl G', 'Dvr L', 'Dvr R']
            One_end_upper_gauge = ['B', 'C','K', 'k','X']
            

            if Quote_name_general in Both_ends_gauge:
                background_color = "green"  # Default color if something goes wrong


                green_min = None
                green_max = None
                if not pd.isna(latest_al_min) or not pd.isna(latest_al_max):
                    green_min = float(latest_al_min) if not pd.isna(latest_al_min) else None
                    green_max = float(latest_al_max) if not pd.isna(latest_al_max) else None
                elif not pd.isna(latest_il_min) or not pd.isna(latest_il_max):
                    green_min = float(latest_il_min) if not pd.isna(latest_il_min) else None
                    green_max = float(latest_il_max) if not pd.isna(latest_il_max) else None
                elif not pd.isna(latest_ial_min) or not pd.isna(latest_ial_max):
                    green_min = float(latest_ial_min) if not pd.isna(latest_ial_min) else None
                    green_max = float(latest_ial_max) if not pd.isna(latest_ial_max) else None

                # Orange Range
                orange_ranges = []
                if not pd.isna(latest_al_min):
                    if not pd.isna(latest_il_min):
                        orange_ranges.append((float(latest_al_min), float(latest_il_min)))
                    elif not pd.isna(latest_ial_min):
                        orange_ranges.append((float(latest_al_min), float(latest_ial_min)))

                if not pd.isna(latest_al_max):
                    if not pd.isna(latest_il_max):
                        orange_ranges.append((float(latest_al_max), float(latest_il_max)))
                    elif not pd.isna(latest_ial_max):
                        orange_ranges.append((float(latest_al_max), float(latest_ial_max)))

                # Pink Range
                pink_ranges = []
                if not pd.isna(latest_ial_min) and not pd.isna(latest_il_min):
                    pink_ranges.append((float(latest_ial_min), float(latest_il_min)))

                if not pd.isna(latest_ial_max) and not pd.isna(latest_il_max):
                    pink_ranges.append((float(latest_ial_max), float(latest_il_max)))

                # Red Range
                red_ranges = []
                if not pd.isna(latest_ial_min):
                    red_ranges.append((float(latest_ial_min) - 10, float(latest_ial_min)))
                if not pd.isna(latest_ial_max):
                    red_ranges.append((float(latest_ial_max), float(latest_ial_max) + 10))

                # Determine the background color of the gauge value based on the latest_value
                if green_min is not None and green_max is not None and green_min <= latest_value <= green_max:
                    background_color = "green"
                elif any(low <= latest_value <= high for low, high in orange_ranges):
                    background_color = "orange"
                elif any(low <= latest_value <= high for low, high in pink_ranges):
                    background_color = "pink"
                elif any(low <= latest_value <= high for low, high in red_ranges):
                    background_color = "red"          


                background_color = None

                if latest_value <= float(latest_ial_min):
                    background_color = "red"
                elif latest_value <= float(latest_il_min):
                    background_color = "pink"
                elif latest_value <= float(latest_al_min):
                    background_color = "orange"
                elif latest_value <= float(latest_al_max):
                    background_color = "green"
                elif latest_value <= float(latest_il_max):
                    background_color = "orange"
                elif latest_value <= float(latest_ial_max):
                    background_color = "pink"
                else:
                    background_color = "red"

                # Create gauge chart
                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=latest_value,
                    number={'font': {'color': background_color}},  # Set the font color to match the background
                    gauge={
                        'axis': {'range': [(float(latest_ial_min)-10) if not pd.isna(latest_ial_min) else 0, 
                                        (float(latest_ial_max)+10) if not pd.isna(latest_ial_max) else 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            *([{'range': [low, high], 'color': "red"} for low, high in red_ranges]),
                            *([{'range': [low, high], 'color': "pink"} for low, high in pink_ranges]),
                            *([{'range': [low, high], 'color': "orange"} for low, high in orange_ranges]),
                            {'range': [green_min, green_max], 'color': "green"} if green_min is not None and green_max is not None else {},
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': latest_value}
                    }
                ))


            elif Quote_name_general in One_end_lower_gauge:
                background_color = "green"  # Default color if something goes wrong

                # Define the color ranges
                green_range = [0, 2000]
                orange_range = [None, None]
                pink_range = [None, None]
                red_range = [None, None]

                # Determine ranges based on the availability of AL_min, IL_min, and IAL_min

                # Green Range (Below AL_min or up to the start of any colored sections)
                if latest_al_min != 0.0:
                    green_range = [0, float(latest_al_min)]
                    orange_range = [float(latest_al_min), (float(latest_al_min)+20)]  
                elif latest_il_min != 0.0:
                    green_range = [0, float(latest_il_min)]
                    pink_range = [float(latest_il_min), (float(latest_il_min)+20)]
                elif latest_ial_min != 0.0:
                    green_range = [0, float(latest_ial_min)]
                    red_range = [float(latest_ial_min), (float(latest_ial_min)+20)]

                # Orange Range (Between AL_min and IL_min or IAL_min or infinity)
                if latest_al_min != 0.0:
                    if latest_il_min != 0.0:
                        orange_range[1] = float(latest_il_min)  # Ends at IL_min if available
                        pink_range = [float(latest_il_min), (float(latest_il_min)+20)]
                    elif latest_ial_min != 0.0:
                        orange_range[1] = float(latest_ial_min)  # Ends at IAL_min if IL_min is not available
                        red_range = [float(latest_ial_min), (float(latest_ial_min)+20)]
                    else:
                        orange_range[1] = (float(latest_al_min)+20)  # Ends at al+20 if neither IL_min nor IAL_min are available

                # Pink Range (Between IL_min and IAL_min)
                if latest_il_min != 0.0:
                    if latest_ial_min != 0.0:
                        pink_range = [float(latest_il_min), float(latest_ial_min)]
                        red_range = [float(latest_ial_min), (float(latest_ial_min)+20)]
                    else:
                        pink_range = [float(latest_il_min), (float(latest_il_min)+20)]  # All remaining space is pink

                # Red Range (Above IAL_min)
                if latest_ial_min != 0.0:
                    red_range = [float(latest_ial_min), (float(latest_ial_min)+20)]  # All remaining space is red

                # Ensure ranges are correctly bounded
                green_range[1] = min(filter(lambda x: x is not None, [green_range[1], orange_range[0], pink_range[0], red_range[0]]))
                orange_range[1] = min(filter(lambda x: x is not None, [orange_range[1], pink_range[0], red_range[0]]))
                pink_range[1] = min(filter(lambda x: x is not None, [pink_range[1], red_range[0]]))

                # Determine the background color of the gauge value based on the latest_value
                if green_range[0] <= latest_value < green_range[1]:
                    background_color = "green"
                elif orange_range[0] is not None and orange_range[0] <= latest_value < orange_range[1]:
                    background_color = "orange"
                elif pink_range[0] is not None and pink_range[0] <= latest_value < pink_range[1]:
                    background_color = "pink"
                elif red_range[0] <= latest_value:
                    background_color = "red"

                # Create gauge chart
                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=latest_value,
                    number={'font': {'color': background_color}}, 
                    gauge={
                        'axis': {'range': [max(0, float(latest_value) - 20), float(latest_ial_min) + 20] if latest_ial_min != 0.0 else [max(0, float(latest_value) - 20), float(latest_value) + 20]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': green_range, 'color': "green"} if green_range[1] is not None else {},
                            {'range': orange_range, 'color': "orange"} if orange_range[1] is not None else {},
                            {'range': pink_range, 'color': "pink"} if pink_range[1] is not None else {},
                            {'range': red_range, 'color': "red"} if red_range[1] is not None else {},
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': latest_value}
                    }
                ))



            elif Quote_name_general in One_end_upper_gauge:
                background_color = "green"  # Default color if something goes wrong

                # Define the color ranges
                green_range = [None, None]
                orange_range = [None, None]
                pink_range = [None, None]
                red_range = [None, None]  # Start with the assumption that everything is green

                # Gauge Range (Overall Range of the Gauge)
                start_value = 0
                if latest_ial_max != 0.0:
                    start_value = float(latest_ial_max) - 20
                elif latest_il_max != 0.0:
                    start_value = float(latest_il_max) - 20
                elif latest_al_max != 0.0:
                    start_value = float(latest_al_max) - 20
                else:
                    start_value = max(0, float(latest_value) - 20)

                # Red Section
                if latest_ial_max != 0.0:
                    red_range = [float(latest_ial_max) - 20, float(latest_ial_max)]

                # Pink Section
                if latest_il_max != 0.0:
                    if latest_ial_max != 0.0:
                        pink_range = [float(latest_ial_max), float(latest_il_max)]
                    else:
                        pink_range = [float(latest_il_max) - 20, float(latest_il_max)]

                # Orange Section
                if latest_al_max != 0.0:
                    if latest_il_max != 0.0:
                        orange_range = [float(latest_il_max), float(latest_al_max)]
                    elif latest_ial_max != 0.0:
                        orange_range = [float(latest_ial_max), float(latest_al_max)]
                    else:
                        orange_range = [float(latest_al_max) - 20, float(latest_al_max)]

                # Green Section
                if latest_al_max != 0.0:
                    green_range = [float(latest_al_max), float(latest_value) + 20]
                elif latest_il_max != 0.0:
                    green_range = [float(latest_il_max), float(latest_value) + 20]
                elif latest_ial_max != 0.0:
                    green_range = [float(latest_ial_max), float(latest_value) + 20]
                else:
                    green_range = [0, float(latest_value) + 20]

                # Ensure ranges are correctly bounded
                red_range[1] = min(filter(lambda x: x is not None, [red_range[1], pink_range[0], orange_range[0], green_range[0]]))
                pink_range[1] = min(filter(lambda x: x is not None, [pink_range[1], orange_range[0], green_range[0]]))
                orange_range[1] = min(filter(lambda x: x is not None, [orange_range[1], green_range[0]]))

                # Determine the background color of the gauge value based on the latest_value
                if red_range[0] <= latest_value < red_range[1]:
                    background_color = "red"
                elif pink_range[0] is not None and pink_range[0] <= latest_value < pink_range[1]:
                    background_color = "pink"
                elif orange_range[0] is not None and orange_range[0] <= latest_value < orange_range[1]:
                    background_color = "orange"
                elif green_range[0] <= latest_value:
                    background_color = "green"

                # Create gauge chart
                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=latest_value,
                    number={'font': {'color': background_color}}, 
                    gauge={
                        'axis': {'range': [start_value, float(latest_value) + 20]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': red_range, 'color': "red"} if red_range[1] is not None else {},
                            {'range': pink_range, 'color': "pink"} if pink_range[1] is not None else {},
                            {'range': orange_range, 'color': "orange"} if orange_range[1] is not None else {},
                            {'range': green_range, 'color': "green"} if green_range[1] is not None else {},
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': latest_value}
                    }
                ))



            else:
                background_color = "green"  
                gauge_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=latest_value,
                    number={'font': {'color': background_color}}, 
                    gauge={
                        'bar': {'color': "darkblue"},
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': latest_value}
                    }
                ))

            

            if len(df_filtered) > 1:
                x_first = df_filtered['Date_control'].iloc[0]
                x_last = df_filtered['Date_control'].iloc[-1]
                y_first = df_filtered['Quote_measured_value'].iloc[0]
                y_last = df_filtered['Quote_measured_value'].iloc[-1]

                time_diff_months = (x_last.year - x_first.year) * 12 + (x_last.month - x_first.month)
                if time_diff_months != 0:
                    slope = (y_last - y_first) / time_diff_months

                if len(df_filtered) > 1:
                    x_second_last = df_filtered['Date_control'].iloc[-2]
                    y_second_last = df_filtered['Quote_measured_value'].iloc[-2]

                    time_diff_last_two_months = (x_last.year - x_second_last.year) * 12 + (x_last.month - x_second_last.month)
                    if time_diff_last_two_months != 0:
                        last_two_points_slope = (y_last - y_second_last) / time_diff_last_two_months

            return fig, gauge_fig, f"Taux de dégradation total: changement de {slope:.2f} par mois", f"Taux de dégradation entre les deux dernières mesures: changement de {last_two_points_slope:.2f} par mois", str(int(loaded_rows) + PAGE_SIZE), f"Valeur la plus récente: {latest_value:.2f}", f"Valeur IAL max la plus récente: {latest_ial_max}", f"Valeur IAL min la plus récente: {latest_ial_min}", f"Valeur IL max la plus récente: {latest_il_max}", f"Valeur IL min la plus récente: {latest_il_min}", f"Valeur AL max la plus récente: {latest_al_max}", f"Valeur AL min la plus récente: {latest_al_min}"

        else:
            return go.Figure(), go.Figure(), "No matching data", "No matching data", loaded_rows, "No matching data", "No matching data", "No matching data", "No matching data", "No matching data", "No matching data"

    except Exception as e:
        logging.error(f"Error in update_graph: {str(e)}")
        fig = go.Figure()
        gauge_fig = go.Figure()
        fig.update_layout(
            title=f'Error: {str(e)}',
            xaxis_title='',
            yaxis_title='',
            showlegend=True
        )
        return fig, gauge_fig, "Error: No data", "Error calculating slopes", loaded_rows, "Error: No data", "Error: No data", "Error: No data", "Error: No data", "Error: No data", "Error: No data"

if __name__ == '__main__':
    app.run_server(debug=True)













[10, 11, 12, 21, 22, 23, 24, 25, 31, 32, 33, 34, 35, 41, 42, 43, 44, 45, 46, 51, 52, 53, 54, 0]