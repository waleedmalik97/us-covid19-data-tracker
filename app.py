import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from urllib.request import urlopen
import json
import pandas as pd
import numpy as np
import time
import datetime
from geopy.geocoders import Nominatim
import ssl
import os

ssl._create_default_https_context = ssl._create_unverified_context




app = dash.Dash(__name__,external_stylesheets=[dbc.themes.MORPH],meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])
app.title = "US Covid-19 Data Tracker"
server = app.server

states = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/COVID-19_Vaccinations_in_the_United_States_Jurisdiction.csv')
county = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/COVID-19_Vaccinations_in_the_United_States_County.csv')
county_trans = os.path.join(os.path.dirname(os.path.abspath(__file__)),'data/United_States_COVID-19_County_Level_of_Community_Transmission_as_Originally_Posted.csv')

df_states = pd.read_csv(states)
df_county = pd.read_csv(county)
df_county_trans = pd.read_csv(county_trans)

df_county.drop(df_county.loc[df_county['FIPS']=='UNK'].index, inplace=True)
df_county.drop(df_county.loc[df_county['Series_Complete_Pop_Pct']==0].index, inplace=True)
df_county.drop(df_county.loc[df_county['FIPS']=='Administered_Dose1_Pop_Pct'].index, inplace=True)

df_county_trans.drop(df_county_trans.loc[df_county_trans['cases_per_100K_7_day_count_change'] == 'suppressed'].index,inplace=True)
df_county_trans.drop(df_county_trans.loc[df_county_trans['percent_test_results_reported_positive_last_7_days'] == 'suppressed'].index,inplace=True)


df_states['Date'] = pd.to_datetime(df_states['Date'])
df_county['Date'] = pd.to_datetime(df_county['Date'])
df_county_trans['report_date'] = pd.to_datetime(df_county_trans['report_date'])

df_county_trans['cases_per_100K_7_day_count_change'] = df_county_trans['cases_per_100K_7_day_count_change'].str.replace(',', '')
df_county_trans['cases_per_100K_7_day_count_change'] = pd.to_numeric(df_county_trans['cases_per_100K_7_day_count_change'])
df_county_trans['percent_test_results_reported_positive_last_7_days'] = pd.to_numeric(df_county_trans['percent_test_results_reported_positive_last_7_days'])

daterange = pd.date_range(start=str(df_states['Date'].iloc[-1]),end=str(df_states['Date'][0]))
df_county_trans.reset_index(inplace=True,drop=True)
daterange_timeseries = pd.date_range(start=str(df_county_trans['report_date'][0]),end=str(df_county_trans['report_date'].iloc[-1]))

def unixTimeMillis(dt):

    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):

    return pd.to_datetime(unix,unit='s')

def getMarks(start, end, Nth=50):

    result = {}
    for i, date in enumerate(daterange):
        if(i%Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%m/%d/%Y'))

    return result

def getMarksTimeseries(start, end, Nth=20):

    result = {}
    for i, date in enumerate(daterange_timeseries):
        if(i%Nth == 1):
            # Append value to dict
            result[unixTimeMillis(date)] = str(date.strftime('%m/%d/%Y'))

    return result


states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}



state_names = []

for state in df_county['Recip_State'].unique():
    state_names.append({'label':states[state],'value':state})



app.layout = dbc.Container(
                           [
                           dbc.Spinner(color='primary',
                           children=[html.Div(id="loading-output",style={'visibility':'hidden'})],
                           fullscreen=True,
                           fullscreen_style={'background-color':'transparent'}),
                            dbc.Row(
                                    [
                                    html.H1(['US Covid-19 Data Tracker'],style={'text-align':'center'}),
                                    html.Hr(style={'background-color':'rgba(61,61,61,0.5)'}),
                                    ],style={'margin-top':'10px'}
                                    ),
                            dbc.Row(
                                    [
                                    dbc.Col(
                                            [
                                            dbc.RadioItems(id='radio-btn1',
                                            options=[
                                                {"label": "Fully Vaccinated", "value": 1},
                                                {"label": "Atleast 1 Dose", "value": 2},
                                            ],
                                            value=1,
                                            inline=True,
                                            )

                                            ],width=3
                                    )
                                    ],style={'padding-left':'80px'},justify="center"
                            ),
                            dbc.Row(id="us-state-map",style={'height':'600px'}
                            ),
                            dbc.Row(
                                    [
                                     dbc.Label(id='state-map-date'),
                                     dcc.Slider(id="slider-us-map",min = unixTimeMillis(daterange.min()),
                                                max = unixTimeMillis(daterange.max()),
                                                value = unixTimeMillis(daterange.max()),
                                                marks=getMarks(daterange.min(),daterange.max()),

                                                )
                                    ],style={'padding':'20px'}
                            ),
                            dbc.Row(
                                    [
                                    html.Hr(style={'background-color':'rgba(61,61,61,0.5)'}),
                                    dbc.Col(
                                            [
                                             dbc.Label("State"),
                                             dcc.Dropdown(
                                             id='state-dropdown',
                                             options=state_names,
                                             value='NY'
                                             )

                                            ],style={'width':'200px'}
                                    ),
                                    dbc.Col(
                                            [
                                            dbc.Label("County"),
                                            dcc.Dropdown(
                                            id='county-dropdown',
                                            value='New York County'
                                            )

                                            ],style={'width':'200px'}
                                    )
                                    ],style={'padding':'40px'}
                            ),
                            dbc.Row(
                                    [
                                    dbc.Col(
                                            [
                                            dbc.Row(
                                                    [
                                                    dbc.Col(
                                                            [
                                                            dbc.RadioItems(id='radio-btn2',
                                                            options=[
                                                                {"label": "Fully Vaccinated", "value": 1},
                                                                {"label": "Atleast 1 Dose", "value": 2},
                                                            ],
                                                            value=1,
                                                            inline=True,
                                                            )

                                                            ],width=5
                                                    )
                                                    ],justify='center'
                                            ),
                                            dbc.Row(
                                            id="us-county-map",style={'height':'900px'}
                                            ),
                                            dbc.Row(
                                                    [
                                                     dbc.Label(id='county-map-date'),
                                                     dcc.Slider(id="slider-us-map-county",
                                                                min = unixTimeMillis(daterange.min()),
                                                                max = unixTimeMillis(daterange.max()),
                                                                value = unixTimeMillis(daterange.max()),
                                                                marks=getMarks(daterange.min(),daterange.max())
                                                               )

                                                    ],style={'padding':'20px'}
                                            )


                                            ],md=6
                                    ),
                                    dbc.Col(
                                            [
                                            dbc.Row(
                                                    [
                                                     dbc.Label(id="timeseries-date"),
                                                     dcc.RangeSlider(id="slider-timeseries",
                                                     min = unixTimeMillis(daterange_timeseries.min()),
                                                     max = unixTimeMillis(daterange_timeseries.max()),
                                                     value = [unixTimeMillis(daterange_timeseries.min()),unixTimeMillis(daterange_timeseries.max())],
                                                     marks=getMarksTimeseries(daterange_timeseries.min(),daterange_timeseries.max()))

                                                    ]
                                            ),
                                            dbc.Row(id="daily-positivity-graph"),
                                            dbc.Row(id="daily-new-cases-graph"),

                                            ],md=6
                                    )
                                    ]
                            ),
                            html.Div(id='hidden-div')


                           ],fluid=True
            )

def create_map(df,state_col,prct_col,lat,long,zoom,text,height,title,geojson_link):
    with urlopen(geojson_link) as response:
        states = json.load(response)

    fig = go.Figure(go.Choroplethmapbox(geojson=states, locations=df[state_col], z=df[prct_col],
                                    colorscale="Viridis",
                                    customdata=df.loc[:, [prct_col]],
                                    text=text,
                                    hovertemplate="<b>%{text}</b><br><br>" +"Percentage: %{customdata[0]}<br>" + "<extra></extra>",
                                    colorbar_title="Percentage %",
                                    marker_opacity=0.5,
                                    marker_line_width=0))
    fig.update_layout(title_text=title,
                      height= height,
                      mapbox_style="carto-positron",
                      mapbox_zoom=zoom, mapbox_center = {"lat": lat, "lon": long})
    return fig



@app.callback(
    [Output('us-state-map','children'),Output('state-map-date','children')],
    [Input('radio-btn1','value'),Input('slider-us-map','value')]
)

def update_state_map(vaccine_status,date):
    date_str = str(unixToDatetime(date))
    date_label = date_str[:10]
    date = pd.to_datetime(date_label)
    df_states_filtered = df_states[df_states['Date'] == date]

    if vaccine_status == 1:

        fig = create_map(df_states_filtered,"Location","Series_Complete_Pop_Pct",37.0902,-95.7129,3,df_states_filtered['Location'],600,"State-level Percentage of Total Population Fully Vaccinated","https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json")
    elif vaccine_status == 2:
        fig = create_map(df_states_filtered,"Location","Administered_Dose1_Pop_Pct",37.0902,-95.7129,3,df_states_filtered['Location'],600,"State-level Percentage of Total Population Vaccinated with atleast 1 Dose","https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/us-states.json")

    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    return [dcc.Graph(figure=fig),"Selected Date: "+datetime.datetime.strptime(date_label, '%Y-%m-%d').strftime('%d %B %Y')]

@app.callback(
    Output('county-dropdown','options'),
    Input('state-dropdown','value')
)

def update_dropdown(state):

    df_county_filtered = df_county[df_county['Recip_State'] == state]
    county_names = []
    for county in df_county_filtered['Recip_County'].unique():
        county_names.append({'label':county,'value':county})
    return county_names

@app.callback(
    [Output('us-county-map','children'),Output('county-map-date','children'),Output('loading-output','style')],
    [
    Input('state-dropdown','value'),
    Input('radio-btn2','value'),
    Input('slider-us-map-county','value'),
    Input('loading-output','style')]
)

def update_county_map(state,vaccine_status,date,loading_style):
    loading_style = {'visibility':'visible'}
    date_str = str(unixToDatetime(date))
    date_label = date_str[:10]
    date = pd.to_datetime(date_label)
    df_county_filtered = df_county[df_county['Recip_State'] == state]
    df_county_filtered_final = df_county_filtered[df_county_filtered['Date'] == date]

    geolocator = Nominatim(user_agent="app.py")
    location = geolocator.geocode(states[state])
    lat = location.latitude
    long = location.longitude

    if vaccine_status == 1:
        fig = create_map(df_county_filtered_final,"FIPS","Series_Complete_Pop_Pct",lat,long,5,df_county_filtered_final['Recip_County'],900,"County-level Percentage of Total Population Fully Vaccinated","https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json")
    elif vaccine_status == 2:
        fig = create_map(df_county_filtered_final,"FIPS","Administered_Dose1_Pop_Pct",lat,long,5,df_county_filtered_final['Recip_County'],900,"County-level Percentage of Total Population Vaccinated with atleast 1 Dose","https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    return [dcc.Graph(figure=fig),"Selected Date: "+datetime.datetime.strptime(date_label, '%Y-%m-%d').strftime('%d %B %Y'),loading_style]

@app.callback(
    [Output('daily-positivity-graph','children'),Output('daily-new-cases-graph','children'),Output('timeseries-date','children')],
    [Input('state-dropdown','value'),Input('county-dropdown','value'),Input('slider-timeseries','value')]
)

def updated_timeseries(state,county,date_range):

    dates = []

    for date in date_range:
        date_str = str(unixToDatetime(date))
        date_label = date_str[:10]
        date = pd.to_datetime(date_label)
        dates.append(date)

    start_date = dates[0]
    end_date = dates[1]

    fig1 = go.Figure()
    fig2 = go.Figure()
    df_county_trans_filtered = df_county_trans[(df_county_trans['county_name'] == county) & (df_county_trans['state_name'] == states[state])]
    df_county_trans_filtered_final = df_county_trans_filtered[(df_county_trans_filtered['report_date'] > start_date) & (df_county_trans_filtered['report_date'] <= end_date)]
    df_county_trans_filtered_final.sort_values('report_date',inplace=True)

    fig1.add_trace(go.Scatter(x=df_county_trans_filtered_final['report_date'], y=df_county_trans_filtered_final['percent_test_results_reported_positive_last_7_days'],
                    mode='lines'))
    fig2.add_trace(go.Scatter(x=df_county_trans_filtered_final['report_date'],y=df_county_trans_filtered_final['cases_per_100K_7_day_count_change'],
                    mode='lines'))
    fig1.update_layout(title_text='Daily % Positivity - 7 Days Moving Average',yaxis=dict(title='Percentage of Positivity'),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    fig2.update_layout(title_text='Daily New Cases - 7 Days Moving Average Per 100k',yaxis=dict(title='Total Number of Cases'),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)")
    fig1.update_xaxes(showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)
    fig1.update_yaxes(showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)
    fig2.update_xaxes(showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)
    fig2.update_yaxes(showline=True, linewidth=1, linecolor='rgba(61,61,61,0.5)',showgrid=False,zeroline=False)

    return [dcc.Graph(figure=fig1),dcc.Graph(figure=fig2),"Selected Date Ranges: "+datetime.datetime.strptime(str(start_date)[:10], '%Y-%m-%d').strftime('%d %B %Y')+" - "+datetime.datetime.strptime(str(end_date)[:10], '%Y-%m-%d').strftime('%d %B %Y')]




if __name__ == "__main__":
    app.run_server(debug=False)
