import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import pandas as pd
from urllib.request import urlopen
import json
import collections

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

########### Define a few variables ######

tabtitle = 'US Census 2017'
sourceurl = 'https://www.kaggle.com/muonneutrino/us-census-demographic-data'
githublink = 'https://github.com/psgrewal42/305-virginia-census-data'
varlist = ['TotalPop', 'Men', 'Women', 'Hispanic',
           'White', 'Black', 'Native', 'Asian', 'Pacific', 'VotingAgeCitizen',
           'Income', 'IncomeErr', 'IncomePerCap', 'IncomePerCapErr', 'Poverty',
           'ChildPoverty', 'Professional', 'Service', 'Office', 'Construction',
           'Production', 'Drive', 'Carpool', 'Transit', 'Walk', 'OtherTransp',
           'WorkAtHome', 'MeanCommute', 'Employed', 'PrivateWork', 'PublicWork',
           'SelfEmployed', 'FamilyWork', 'Unemployment', 'RUCC_2013']

loading_style = {'position': 'relative', 'align-self': 'center'}

df = pd.read_pickle('resources/va-stats.pkl')
all_counties = pd.read_csv(
    'https://raw.githubusercontent.com/austinlasseter/dash-virginia-counties/master/resources/acs2017_county_data.csv')
usda = pd.read_excel(
    'https://github.com/austinlasseter/dash-virginia-counties/raw/master/resources/ruralurbancodes2013.xls')
all_counties_extended = pd.merge(all_counties, usda, left_on='CountyId', right_on='FIPS', how='left')
all_counties_extended['fips'] = all_counties_extended['FIPS'].astype(str)

mid_lat_long = {'Wisconsin': [44.5, -89.5], 'West Virginia': [39, -80.5], 'Vermont': [44, -72.699997],
                'Texas': [31, -100], 'South Dakota': [44.5, -100], 'Rhode Island': [41.742325, -71.742332],
                'Oregon': [44, -120.5], 'New York': [43, -75], 'New Hampshire': [44, -71.5], 'Nebraska': [41.5, -100],
                'Kansas': [38.5, -98], 'Mississippi': [33, -90], 'Illinois': [40, -89], 'Delaware': [39, -75.5],
                'Connecticut': [41.599998, -72.699997], 'Arkansas': [34.799999, -92.199997],
                'Indiana': [40.273502, -86.126976], 'Missouri': [38.573936, -92.60376],
                'Florida': [27.994402, -81.760254], 'Nevada': [39.876019, -117.224121],
                'Maine': [45.367584, -68.972168], 'Michigan': [44.182205, -84.506836],
                'Georgia': [33.247875, -83.441162], 'Hawaii': [19.741755, -155.844437],
                'Alaska': [66.160507, -153.369141], 'Tennessee': [35.860119, -86.660156],
                'Virginia': [37.926868, -78.024902], 'New Jersey': [39.833851, -74.871826],
                'Kentucky': [37.839333, -84.27002], 'North Dakota': [47.650589, -100.437012],
                'Minnesota': [46.39241, -94.63623], 'Oklahoma': [36.084621, -96.921387],
                'Montana': [46.96526, -109.533691], 'Washington': [47.751076, -120.740135],
                'Utah': [39.41922, -111.950684], 'Colorado': [39.113014, -105.358887], 'Ohio': [40.367474, -82.996216],
                'Alabama': [32.31823, -86.902298], 'Iowa': [42.032974, -93.581543],
                'New Mexico': [34.307144, -106.018066], 'South Carolina': [33.836082, -81.163727],
                'Pennsylvania': [41.203323, -77.194527], 'Arizona': [34.048927, -111.093735],
                'Maryland': [39.045753, -76.641273], 'Massachusetts': [42.407211, -71.382439],
                'California': [36.778259, -119.417931], 'Idaho': [44.068203, -114.742043],
                'Wyoming': [43.07597, -107.290283], 'North Carolina': [35.782169, -80.793457],
                'Louisiana': [30.39183, -92.329102]}
statelist = mid_lat_long.keys()

df_dict = {}

for state in statelist:
    dfs = all_counties_extended.loc[all_counties_extended['State_x'] == state]
    df_dict[state] = dfs

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = tabtitle

########### Layout

app.layout = html.Div(children=[
    html.H3('USA Census 2017'),
    # Dropdowns
    html.Div(children=[
        html.Div([
            html.H6('Select the state:'),
            dcc.Dropdown(
                id='state-drop',
                options=[{'label': i, 'value': i} for i in statelist],
                value='Virginia'
            ),
            html.Br(),
            html.H6('Select census variable:'),
            dcc.Dropdown(
                id='stats-drop',
                options=[{'label': i, 'value': i} for i in varlist],
                value='MeanCommute'
            ),
        ], className='three columns'),

        html.Br(),
        # right side
        html.Div([
            dcc.Loading(id='loading', parent_style=loading_style, children=[dcc.Graph(id='va-map'), ]),

        ], className='nine columns'),
    ], className='twelve columns'),

    # Footer
    html.Br(),
    html.A('Code on Github', href=githublink),
    html.Br(),
    html.A("Data Source", href=sourceurl),
]
)


############ Callbacks
@app.callback([Output('va-map', 'figure'), Output('loading', 'parent_style')],
              [Input('stats-drop', 'value'), Input('state-drop', 'value')])
def display_results(selected_value, selected_state):
    new_loading_style = loading_style
    #dfs = all_counties_extended.loc[all_counties_extended['State_x'] == selected_state]
    dfs = df_dict[selected_state]
    if selected_value not in list(df.select_dtypes(['category']).columns):
        valmin = dfs[selected_value].min()
        valmax = dfs[selected_value].max()
        fig = go.Figure(go.Choroplethmapbox(geojson=counties,
                                            locations=dfs['FIPS'],
                                            z=dfs[selected_value],
                                            colorscale='Earth',
                                            text=dfs['County'],
                                            zmin=valmin,
                                            zmax=valmax,
                                            marker_line_width=0))

    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=5,
                      mapbox_center={"lat": mid_lat_long[selected_state][0], "lon": mid_lat_long[selected_state][1]})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig, new_loading_style


############ Deploy
if __name__ == '__main__':
    app.run_server(debug=True)
