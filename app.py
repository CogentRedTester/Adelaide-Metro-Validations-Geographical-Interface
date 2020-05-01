#Available at: https://gitlab.com/RedTester/adelaide-metro-validations-geographic-interface

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_colorscales
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.offline
from plotly.offline import iplot
import plotly.express as px
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from textwrap import dedent as d
import time

mapbox_access_token = 'TOKEN'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

metro3 = pd.read_csv('../2016-2018_Metro_sorted_removed_columns.csv')
stopList = pd.read_csv('../stops_removed_columns.csv')

metro3.stop_id.fillna(-1, inplace = True)
metro3.ROUTE_CODE.fillna('N/A', inplace = True)

metro3.VALIDATION_DATE = pd.to_datetime(metro3['VALIDATION_DATE'])

weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


colourscale = px.colors.sequential.Viridis


route_list = metro3.ROUTE_CODE.unique()

route_options = [{'label': i, 'value': i} for i in route_list] #list comprehension


date_list = pd.Series(metro3.VALIDATION_DATE.unique())
date_list_original = pd.Series(metro3.VALIDATION_DATE.unique())

filterOne = metro3
filterTwo = filterOne
filterThree = filterTwo
filterFour = filterThree
filterFive = stopList

app.layout = html.Div([
    
    html.Div(className="row", children =[

        html.Div([

            dcc.Markdown('''
                ### Filter Heatmap
                '''),

            html.Label('Filter Vehicle Type'),
            dcc.RadioItems(
                id = 'vehicle_selector',
                options = [
                {'label' : 'All', 'value' : 0},
                {'label' : 'Bus', 'value' : 1},
                {'label' : 'Tram', 'value' : 4},
                {'label' : 'Train', 'value' : 5}
                ],
                value = 0,
                labelStyle={'display': 'inline-block'},
            ),

            html.Label('Filter Route'),
            dcc.Dropdown(
                id = 'route_filter',
                options= route_options,
                multi=True,
            ),

            html.Label('Filter by Validation Medium'),
            dcc.RadioItems(
                id = 'medium_selector',
                options = [
                {'label' : 'Both |', 'value' : 0},
                {'label' : 'Card |', 'value' : 1},
                {'label' : '% Card |', 'value' : 2},
                {'label' : 'Ticket |', 'value' : 3},
                {'label' : '% Ticket', 'value' : 4}
                ],
                value = 0,
                labelStyle = {'display' : 'inline-block'},
            ),

            html.Label('Filter Time Range'),

            html.Div([
                dcc.RangeSlider(
                    id='date_slider',
                    min = 0,
                    max = date_list.index.max(),
                    value = [0, date_list.index.max()],
                    #marks = getMarks(),
                    updatemode = 'drag',
                    allowCross = False,
                    
                )
            ], style={'marginLeft': 10, 'marginBottom': 25}),

            html.Div([

                dcc.Loading(
                    id="loading",
                    children=[html.Div([
                        html.Button(id = 'skip_back', n_clicks = 0, children = 'skip-back'),
                        html.Button(id = 'skip_forward', n_clicks = 0, children = 'skip-forward'),
                        html.Button(id='submit-button', n_clicks=0, children='Submit')
                    ])],
                    type="circle",
                ),
                html.P('skipping maintains the current date range'),

                dcc.Markdown(id = 'range_text'),
            ]),

            dcc.Graph(
                id='metro_density',
            ),

            html.Label('Change colorscale range'),
            html.Div([
                dcc.RangeSlider(
                    id = 'color_slider',
                    min = 0,
                    max = 1000000,
                    value = [0, 200000],
                    allowCross = False,
                    updatemode = 'drag',
                )
            ], style={'marginLeft': 5, 'marginBottom': 25}),

            html.Pre('stops with validations below the minimum will have no color, stops above the max will be capped'),

            


        ], className="six columns"),
        

        html.Div([
            #html.H3('Column 1'),
            dcc.Markdown(d("""
                ### Detailed Stop Info

                Click on points on the map or use the search box to select stops.
            """)),

            html.Div('', style={'padding': 12}),

            dcc.Dropdown(
                id = 'stop_dropdown'
            ),

            dcc.Markdown(id = 'stop_name'),
            html.P(id = 'stop_description'),
            html.P(id = 'stop_id'),
            html.P(id = 'stop_coords'),
            html.P(id = 'stop_url'),
            html.P(id = 'total_usage'),
            html.P(id = 'stop_numbers'),
            html.P(id = 'unknown_validations'),

            dcc.Graph(
                id='route_composition'
            ),

            dcc.Graph(
                id = 'line_graph'
            )
        ], className="six columns"),


    ]),

    html.Div(id='filterOne', style={'display': 'none'}, children = 0),
    html.Div(id='GraphUpdated', style={'display': 'none'}, children = 0)
])

#loading bar
@app.callback(
    Output("submit-button", "children"),
    [Input("route_filter", "value"), Input('route_filter', 'options'), Input('vehicle_selector', 'value'), Input('medium_selector', 'value')])
def input_triggers_nested(value, options, value2, medium):
    time.sleep(1)
    return 'Submit'


#vehicle selection filter
#sets the options for the route dropdown
@app.callback(
    Output('route_filter', 'options'),
    [Input('vehicle_selector', 'value')])
def vehicle_selector(value):
    global filterOne

    if (value == 0):
        filterOne = metro3
    else:
        filterOne = metro3[metro3['NUM_MODE_TRANSPORT'] == value]

    route_list = filterOne.ROUTE_CODE.unique()
    route_options = [{'label': i, 'value': i} for i in route_list] #list comprehension
    return route_options
   

#filters the dataset to just use the routes selected in the searchbox/dropdown
#increments the integer in filterOne which triggers the medium filter callback to run
@app.callback(
    Output('filterOne', 'children'),
    [Input('route_filter', 'value'), Input('route_filter', 'options')],
    [State('filterOne', 'children')])
def filter_routes(route_value, route_options, filter1):
    global filterOne
    global filterTwo

    if ((route_value is None) | (route_value == [])):
        filterTwo = filterOne
    else:
        filterTwo = filterOne[filterOne['ROUTE_CODE'].isin(route_value)]
    
    return filter1 + 1

#metrocard vs ticket (medium) selector
#as this is the last filter before the slider it also finds the valid dates to populate the slider with
@app.callback(
    Output('date_slider', 'marks'),
    [Input('medium_selector', 'value'), Input('filterOne', 'children')])
def filterByMedium(medium, filter1):

    global filterTwo
    global filterThree
    global date_list
    global date_list_original

    if (medium == 0) | (medium == 4) | (medium == 2):
        filterThree = filterTwo
    elif medium == 1:
        filterThree = filterTwo[filterTwo['MEDIUM_TYPE'] == 1]
    elif medium == 3:
        filterThree = filterTwo[filterTwo['MEDIUM_TYPE'] == 3]

    date_list = pd.Series(filterThree.VALIDATION_DATE.unique())

    minIndex = date_list_original[date_list_original == date_list.min()].index[0]
    maxIndex = date_list_original[date_list_original == date_list.max()].index[0]

    #algorithm to set labels under the slider
    #adds 4 per year, with the first replacing Jan with the year.
    #always adds a label for the first date in the set
    #if more than 135 days go by without any labels then the next valid day will have a label no matter what
    lastLabel = 0
    result = {}
    for i in range(len(date_list_original)):
        if (date_list == date_list_original[i]).any():
            # Append value to dict
            result[i] = ''

            if ((lastLabel == 0) & (i != 0)):
                result[i] = str(date_list_original[i].day) + "/" + str(date_list_original[i].month)
                lastLabel = i + 1
            elif (i - lastLabel > 135):
                result[i] = str(date_list_original[i].day) + "/" + str(date_list_original[i].month)
                lastLabel = i + 1
            elif (date_list_original[i].dayofyear == 1):
                result[i] = str(date_list_original[i].year)
                lastLabel = i + 1
            else:
                if ((date_list_original[i].month % 3 == 1) & (date_list_original[i].day == 1)):
                    result[i] = months[date_list_original[i].month - 1]
                    lastLabel = i + 1

    return result

#buttons for moving the date range
@app.callback(
    Output('date_slider', 'value'),
    [Input('skip_forward', 'n_clicks'), Input('skip_back', 'n_clicks')],
    [State('date_slider', 'value'), State('date_slider', 'min'), State('date_slider', 'max')])
def skip_forward(n_clicks, n_clicks2, value, min, max):
    date_range = 1 + value[1] - value[0]

    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if ((n_clicks == 0) & (n_clicks2 == 0)):
        return value

    if (button_id == 'skip_forward'):
        value[0] += date_range
        value[1] += date_range
    elif (button_id == 'skip_back'):
        value[0] = value[0] - date_range
        value[1] = value[1] - date_range

    if (value[0] < min):
        value[0] = min
    elif (value[0] > max):
        value[0] = max

    if (value[1] > max):
        value[1] = max
    elif (value[1] < min):
        value[1] = min

    return value

#text showing the date of the current date range
@app.callback(
    Output('range_text', 'children'),
    [Input('date_slider', 'value')])
def print_slider_range(value):
    global weekdays
    global months

    min = str(weekdays[date_list_original[value[0]].dayofweek]) + " " + str(date_list_original[value[0]].day) + " " + str(months[date_list_original[value[0]].month - 1]) + " " + str(date_list_original[value[0]].year)
    max = str(weekdays[date_list_original[value[1]].dayofweek]) + " " + str(date_list_original[value[1]].day) + " " + str(months[date_list_original[value[1]].month - 1]) + " " + str(date_list_original[value[1]].year)

    return  "### " + min + " - " + max


#creates colour slider marks below the slider ends
@app.callback(
    Output('color_slider', 'marks'),
    [Input('color_slider', 'value')])
def update_color_slider_marks(value):
    result = {}

    result[value[0]] = str(value[0])
    
    if (value[1] - value[0] > 30000):
        result[value[1]] = str(value[1])
    else:
        result[value[1] + (30000 - (value[1] - value[0]))] = str(value[1])

    return result


#creating the graph
@app.callback(
    [Output('metro_density', 'figure'), Output('stop_dropdown', 'options'), Output('GraphUpdated', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('date_slider', 'value'), State('medium_selector', 'value'), State('color_slider', 'value'), State('GraphUpdated', 'children')])
def filter_time_draw_figure(n_clicks, value, medium, color_value, graphUpdated):
    global filterTwo
    global filterThree
    global filterFour
    global filterFive
    global date_list

    date_list = pd.Series(date_list)

    oneDay = pd.Timedelta(days=1)

    filterFour = filterThree[(filterThree['VALIDATION_DATE'] > (date_list_original[value[0]] - oneDay)) & (filterThree['VALIDATION_DATE'] < (date_list_original[value[1]] + oneDay))]

    df = filterFour.groupby('stop_id').sum()[['USAGE']].reset_index()
    df = pd.merge(df, stopList, how="left", on="stop_id")
    df.stop_id = df.stop_id.astype(int)

    df.stop_name.fillna(df.stop_id.astype(str), inplace=True)

    stop_list = []
    
    for index, row in df.iterrows():
        if (row.stop_id == -1):
            stop_list.append({'label': 'N/A', 'value': row.stop_id})
        else:
            stop_list.append({'label': row.stop_name, 'value': row.stop_id})
    
    if (medium == 2):
        cardFiltered = filterFour[filterFour['MEDIUM_TYPE'] == 1]
        cardFiltered = cardFiltered.groupby('stop_id').sum()[['USAGE']].reset_index()
        cardFiltered = pd.DataFrame(cardFiltered).rename(columns={'USAGE':'USAGE_CARD'})
        df = pd.merge(df, cardFiltered, how = 'left', on = 'stop_id')
        df.USAGE_CARD = df.USAGE_CARD.replace('N/A', 0)
        df.USAGE = (df.USAGE_CARD / df.USAGE) * 100
    elif (medium == 4):
        ticketFiltered = filterFour[filterFour['MEDIUM_TYPE'] == 3]
        ticketFiltered = ticketFiltered.groupby('stop_id').sum()[['USAGE']].reset_index()
        ticketFiltered = pd.DataFrame(ticketFiltered).rename(columns={'USAGE':'USAGE_TICKET'})
        df = pd.merge(df, ticketFiltered, how = 'left', on = 'stop_id')
        df.USAGE_TICKET = df.USAGE_TICKET.replace('N/A', 0)
        df.USAGE = (df.USAGE_TICKET / df.USAGE) * 100

    
    filterFive = df

    site_lat = df.stop_lat
    site_lon = df.stop_lon
    usage = df.USAGE
    locations_name = df.stop_name
    stop_ids = df.stop_id
    hover = locations_name + " | Usage: " + usage.astype(str)


    showRatio = False
    showDensity = True;

    if (medium == 2) | (medium == 4):
        showRatio = True
        showDensity = False


    t1 = go.Scattermapbox(
        lat=site_lat,
        lon=site_lon,
        meta = stop_ids,
        mode='markers',
        opacity = 1,
        visible = showRatio,
        unselected = dict(
            marker = dict(
                opacity = 0.3,
            )
        ),
        marker=dict(
            size = 25,
            color=usage,
            opacity = 0.3,
            cmax=100,
            cmin=0,
            colorscale = colourscale,
            #autocolorscale = True,
            showscale = True,
            colorbar = dict(
                len = 0.8,
            ),
        ),
        
    )

    t2 = go.Densitymapbox(
            lat = site_lat,
            lon = site_lon,
            z = usage,
            autocolorscale = False,
            colorscale = colourscale,
            visible = showDensity,
            colorbar = dict(
                len = 0.9,
            ),
            radius = 20,
            meta = locations_name,
            text = locations_name,
            hoverinfo = 'text+z',
            name = "heatmap",
            zmin = color_value[0],
            zmax = color_value[1],
        )

    t3 = go.Scattermapbox(
                    lat=site_lat,
                    lon=site_lon,
                    meta = stop_ids,
                    mode='markers',
                    marker=dict(
                        size = 5,
                        color = 'black',
                        opacity = 0.7,
                        colorscale = 'Viridis',
                    ),
                    unselected = dict(
                        marker = dict(
                            opacity = 0.7,
                        )
                    ),
                    hovertext=hover,
                    hoverinfo = "text",
                    name="stops",
                )
    fig = {
                'data': [t1, t2, t3],
                'layout': go.Layout(
                    autosize=False,
                    width = 900,
                    height = 700,
                    margin = dict(
                        t = 15,
                        b = 50,
                        r = 50,
                        l = 10
                    ),
                    hovermode='y',
                    clickmode = 'event+select',
                    showlegend=True,
                    #showScale=True,
                    uirevision = 24,
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        bearing=0,
                        center=dict(
                            lat=-35,
                            lon=138.6
                        ),
                        pitch=0,
                        zoom=9,

                    ),
                )
        }

    return fig, stop_list, graphUpdated + 1

#sets the dropdown to be the clickdata stop
@app.callback(
    Output('stop_dropdown', 'value'),
    [Input('metro_density', 'clickData')])
def selectStop(clickData):
    if clickData is None:
        stopID = ''
    else:
        stopID = clickData['points'][0]['meta']

    return stopID

#creates the clicked stop info text
@app.callback(
    [Output('stop_name', 'children'), Output('stop_description', 'children'), Output('stop_id', 'children'),
    Output('total_usage', 'children'), Output('stop_coords', 'children'),
    Output('stop_url', 'children'), Output('stop_numbers', 'children'), Output('unknown_validations', 'children')],
    [Input('stop_dropdown', 'value'), Input('GraphUpdated', 'children')])
def display_click_data(stopID, graph):
    global filterFive
    global filterFour

    if stopID is not None:
        stop = filterFive[filterFive['stop_id'] == stopID].reset_index()
        if (len(stop) < 1):
            globalStats = True
        else:
            globalStats = False
    else:
        globalStats = True

    if (stopID == '') | (stopID is None) | globalStats:
        name = ''
        stopID = 'No stops selected'
        description = 'Global stats for current filter:'
        total_usage = 'Total usage: ' + str(int(metro3['USAGE'].sum()))
        filtered_usage = 'Filtered usage: ' + str(int(filterFour['USAGE'].sum()))
        coords = ''
        parent = ''
        url = ''
        stopNumbers = "Number of stops found with current filters: " + str(len(filterFive)) + "   |   Number of unknown stops: " + str(filterFive.stop_lat.isnull().sum())
        unknown_validations = ''

        if (graph != 0):
            unknown_validations = "Number of validations missing from heatmap: " + str(filterFive[filterFive['stop_lat'].isnull()]['USAGE'].sum())

    else:
        name = ""
        description = 'Stop desc: ' + str(stop.iloc[0]['stop_desc'])
        total_usage = 'Total usage of stop: ' + str(metro3[metro3['stop_id'] == stopID]['USAGE'].sum())
        filtered_usage = 'Filtered usage of stop: ' + str(int(filterFour[filterFour['stop_id'] == stopID]['USAGE'].sum()))
        coords = "Lat: " + str(stop.iloc[0]['stop_lat']) + "   |   Lon: " + str(stop.iloc[0]['stop_lon'])
        url = "URL: " + str(stop.iloc[0]['stop_url'])
        parent = "Parent station: " + str(stop.iloc[0]['parent_station'])
        stopNumbers = ''
        unknown_validations = ''

        if (stopID == -1):
            stopID = 'N/A'

        stopID = "Stop ID: " + str(stopID) + "   |   Stop Code: " + str(stop.iloc[0]['stop_code']) + "   |   " + parent

    return name, description, stopID, total_usage + "   |   " + filtered_usage, coords, url, stopNumbers, unknown_validations

#creates the per stop route bar graph
@app.callback(
    Output('route_composition', 'figure'),
    [Input('stop_dropdown', 'value'), Input('GraphUpdated', 'children')])
def route_composition_graph(stop, graph):

    data = filterFour[filterFour['stop_id'] == stop]

    data = data.groupby('ROUTE_CODE').sum()[['USAGE']].reset_index()
    fig = go.Figure([go.Bar(x = data.index, y = data.USAGE, text = data.USAGE, textposition = 'auto')])
    fig.update_layout(
        width = 900,
        height = 450,
        xaxis = dict(
                tickmode = 'array',
                tickvals = data.index,
                ticktext = data.ROUTE_CODE),
        title=go.layout.Title(
                text="Filtered Usage by Route",
                )
        )
    return fig

#draws the line graph of usage per route
@app.callback(
    Output('line_graph', 'figure'),
    [Input('stop_dropdown', 'value'), Input('GraphUpdated', 'children')])
def route_line_graph(stop, graph):

    data = filterFour[filterFour['stop_id'] == stop]

    routes = data.ROUTE_CODE.unique()

    fig = go.Figure()

    #creates traces for each route at the stop and adds them to the figure
    for route in routes:
        route_data = data[data['ROUTE_CODE'] == route].groupby('VALIDATION_DATE').sum()[['USAGE']]
        
        #filling in extra dates as 0 so that the line connecting the points does not float above the x axis
        route_data = route_data.asfreq('D')
        route_data = route_data.reset_index()
        route_data.USAGE.fillna(0, inplace=True)
        
        trace = go.Scatter(
            x = route_data.VALIDATION_DATE,
            y = route_data.USAGE,
            name = route,
            marker = dict(
                line = dict(
                    width = 1,
                )
            )
        )
        fig.add_trace(trace)

    fig.update_layout(
        title_text = 'Filtered Route Usage Over Time',
        xaxis_rangeslider_visible=True,
        width = 900,
        height = 450,
        showlegend = True,
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
