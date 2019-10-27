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
import codecs, json

mapbox_access_token = 'pk.eyJ1IjoiZ2hjYXJuZWlybyIsImEiOiJjazBmOXNjNmswcWcyM2JxZXhjNzc2eDBkIn0.L4pHZaHSpa4pQL-fML9i5w'

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

#metro = pd.read_csv('stops_3Dates.csv')
metro3 = pd.read_csv('../2016-2018_Metro_data_sorted_and_cleaned.csv').rename(columns={'GTFS_ID':'stop_id'})
stopList = pd.read_csv('../stops.csv')

metro3.VALIDATION_DATE = pd.to_datetime(metro3['VALIDATION_DATE'])
metro3.USAGE += 4

weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

#print(metro3[0]['VALIDATION_DATE'].date())

#metro = metro.drop(14)
#site_lat = metro.stop_lat
#site_lon = metro.stop_lon
#locations_name = metro.stop_name
#usage = metro['2016-03-01']
#colourscale = [[0, 'rgb(0,0,0)'], [1, 'rgb(255,0,0)']]



colourscale = px.colors.sequential.Viridis
'''
= [
        [0, 'rgb(250, 250, 250)'],        #0
        [1.0/10000.0, 'rgb(200, 200, 200)'], #10
        [1.0/1000.0, 'rgb(150, 150, 150)'],  #100
        [1.0/100.0, 'rgb(100, 100, 100)'],   #1000
        [1.0/10.0, 'rgb(50, 50, 50)'],       #10000
        [1, 'rgb(0, 0, 0)']             #100000

    ]
'''

#optionsD = np.array([[metro.stop_name], [metro.USAGE]])


colourscale2 = {'#440154',
 '#482878',
 '#3e4989',
 '#31688e',
 '#26828e',
 '#1f9e89',
 '#35b779',
 '#6ece58',
 '#b5de2b',
 '#fde725'}

route_list = metro3.ROUTE_CODE.unique()
route_options = [{'label': i, 'value': i} for i in route_list] #list comprehension


date_list = pd.Series(metro3.VALIDATION_DATE.unique())
date_list_original = pd.Series(metro3.VALIDATION_DATE.unique())
#dates = pd.to_datetime()

filterOne = metro3
filterTwo = filterOne
filterThree = filterTwo
filterFour = filterThree
filterFive = filterFour


#following code taken from https://stackoverflow.com/questions/51063191/date-slider-with-plotly-dash-does-not-work/51099170#51099170
def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='s')



'''
                min = unixTimeMillis(daterange.min()),
                max = unixTimeMillis(daterange.max()),
                value = [unixTimeMillis(daterange.min()),
                         unixTimeMillis(daterange.max())],
                marks=getMarks(daterange.min(),
                            daterange.max()),
                            '''




app.layout = html.Div([
    
    html.Div(className="row", children =[

        html.Div([
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
            dcc.RangeSlider(
                id='date_slider',
                min = 0,
                max = date_list.index.max(),
                value = [0, date_list.index.max()],
                #marks = getMarks(),
                updatemode = 'drag',
                allowCross = False,
            ),

            html.Div('', style={'padding': 12}),

            html.Div([

                dcc.Loading(
                    id="loading",
                    children=[html.Div([
                        html.Button(id = 'skip_back', n_clicks = 0, children = '<'),
                        html.Button(id = 'skip_forward', n_clicks = 0, children = '>'),
                        html.Button(id='submit-button', n_clicks=0, children='Submit')
                    ])],
                    type="circle",
                ),

                html.Pre(id = 'range_text', style={'padding': 20}),
            ]),

            

            

            

            dcc.Graph(
                id='metro_density',
            ),

            dcc.RangeSlider(
                id = 'color_slider',
                min = 0,
                max = 1000000,
                value = [0, 200000],
                allowCross = False,
                updatemode = 'drag',
            ),

            html.Div('', style={'padding': 12}),


        ], className="six columns"),
        

        html.Div([
            #html.H3('Column 1'),
            dcc.Markdown(d("""
                **Click Data**

                Click on points in the graph.
            """)),
            html.Pre(id='click-data', style=styles['pre']),
            dcc.Graph(
                id='stop_info'
            )
        ], className="six columns"),


    ]),

    dash_table.DataTable(
        id = 'table'
    ),

    html.Div(id='filterOne', style={'display': 'none'}, children = 0),
    html.Div(id='filterTwo', style={'display': 'none'}, children = ''),
    html.Div(id='filterThree', style={'display': 'none'}, children = ''),

])

'''
@app.callback(
    Output('date_slider', 'value'),
    [Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date')])
def update_slider(start_date, end_date):
    print (start_date)
    print (end_date)
    return [dates[dates == start_date].index[0], dates[dates == end_date].index[0]]

@app.callback(
    [Output('date-picker-range', 'start_date'), Output('date-picker-range', 'end_date')],
    [Input('date_slider', 'value')])
def update_start_date(value):
    return date_list_original[value[0]], date_list_original[value[1]]
'''

#loading bar
@app.callback(
    Output("submit-button", "children"),
    [Input("route_filter", "value"), Input('route_filter', 'options'), Input('vehicle_selector', 'value'), Input('medium_selector', 'value')])
def input_triggers_nested(value, options, value2, medium):
    time.sleep(1)
    return 'Submit'


#vehicle selection filter
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
    print(value)
    return route_options
   

#filters the dataset to just use the routes selected in the searchbox/dropdown
#filters the data by date for the range slider
@app.callback(
    Output('filterOne', 'children'),
    [Input('route_filter', 'value'), Input('route_filter', 'options')],
    [State('filterOne', 'children')])
def filter_routes(route_value, route_options, filter1):
    print("filter updated")
    print(route_value)

    global filterOne
    global filterTwo

    

    if ((route_value is None) | (route_value == [])):
        filterTwo = filterOne
    else:
        print(filterTwo.head())
        filterTwo = filterOne[filterOne['ROUTE_CODE'].isin(route_value)]
    
    return filter1 + 1

#metrocard vs ticket selector
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

#buttons for mvoing the date range
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

#text showing the date of the current range
@app.callback(
    Output('range_text', 'children'),
    [Input('date_slider', 'value')])
def print_slider_range(value):
    global weekdays
    global months

    min = str(weekdays[date_list_original[value[0]].dayofweek]) + " " + str(date_list_original[value[0]].day) + " " + str(months[date_list_original[value[0]].month - 1]) + " " + str(date_list_original[value[0]].year)
    max = str(weekdays[date_list_original[value[1]].dayofweek]) + " " + str(date_list_original[value[1]].day) + " " + str(months[date_list_original[value[1]].month - 1]) + " " + str(date_list_original[value[1]].year)

    return  min + " - " + max

#creating the graph
@app.callback(
    Output('metro_density', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('date_slider', 'value'), State('medium_selector', 'value'), State('color_slider', 'value')])
def filter_time_draw_figure(n_clicks, value, medium, color_value):
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

    if (medium == 2):
        cardFiltered = filterFour[filterFour['MEDIUM_TYPE'] == 1]
        cardFiltered = cardFiltered.groupby('stop_id').sum()[['USAGE']].reset_index()
        cardFiltered = pd.DataFrame(cardFiltered).rename(columns={'USAGE':'USAGE_CARD'})
        df = pd.merge(df, cardFiltered, how = 'left', on = 'stop_id')
        print(df.head())
        df.USAGE_CARD = df.USAGE_CARD.replace('N/A', 0)
        df.USAGE = (df.USAGE_CARD / df.USAGE) * 100
        print(df.head())
    elif (medium == 4):
        ticketFiltered = filterFour[filterFour['MEDIUM_TYPE'] == 3]
        ticketFiltered = ticketFiltered.groupby('stop_id').sum()[['USAGE']].reset_index()
        ticketFiltered = pd.DataFrame(ticketFiltered).rename(columns={'USAGE':'USAGE_TICKET'})
        df = pd.merge(df, ticketFiltered, how = 'left', on = 'stop_id')
        print(df.head())
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
               # tick0 = 0,
              #  tickmode = 'array',
             #   tickvals = [0, 1000, 10000, 100000]
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
                        #color=usage,
                        color = 'black',
                        opacity = 0.7,
                        #cmax=2000000,
                        #cmin=0,
                        colorscale = 'Viridis',
                        #showscale = True,
                    ),
                    unselected = dict(
                        marker = dict(
                            opacity = 0.7,
                        )
                    ),
                    hovertext=hover,
                    hoverinfo = "text",
                    #hoverinfo="text",
                    
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

    return fig


@app.callback(
    [Output('table', 'columns'), Output('table', 'data')],
    [Input('metro_density', 'figure')])
def createTable(n_clicks):
    global filterFive
    columns = [{"name": i, "id": i} for i in filterFive.columns]
    return columns, filterFive.to_dict('records')


#creates the point info text box
@app.callback(
    Output('click-data', 'children'),
    [Input('metro_density', 'clickData')])
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)

#creates the per stop route bar graph
@app.callback(
    Output('stop_info', 'figure'),
    [Input('metro_density', 'clickData')])
def selected_stop_graph(clickData):
    data = filterFour[filterFour['stop_id'] == clickData['points'][0]['meta']].copy()
    #data.USAGE = data.USAGE + 4
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
                text="Routes at " + clickData['points'][0]['hovertext'],
                )
        )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')