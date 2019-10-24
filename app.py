import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
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

#print(metro3[0]['VALIDATION_DATE'].date())

#metro = metro.drop(14)
#site_lat = metro.stop_lat
#site_lon = metro.stop_lon
#locations_name = metro.stop_name
#usage = metro['2016-03-01']
#colourscale = [[0, 'rgb(0,0,0)'], [1, 'rgb(255,0,0)']]



colourscale = [
        [0, 'rgb(250, 250, 250)'],        #0
        [1.0/10000.0, 'rgb(200, 200, 200)'], #10
        [1.0/1000.0, 'rgb(150, 150, 150)'],  #100
        [1.0/100.0, 'rgb(100, 100, 100)'],   #1000
        [1.0/10.0, 'rgb(50, 50, 50)'],       #10000
        [1, 'rgb(0, 0, 0)']             #100000

    ]


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
#dates = pd.to_datetime()

filterOne = metro3
filterTwo = filterOne
filterThree = filterTwo
filterFour = filterThree


#following code taken from https://stackoverflow.com/questions/51063191/date-slider-with-plotly-dash-does-not-work/51099170#51099170
def unixTimeMillis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))

def unixToDatetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix,unit='s')

def getMarks(Nth=120):
    ''' Returns the marks for labeling. 
        Every Nth value will be used.
    '''

    result = {}
    for i in range(len(date_list)):
        if(i%Nth == 1):
            # Append value to dict
            result[i] = str(date_list[i].date())

    return result

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

            dcc.Dropdown(
                id = 'route_filter',
                options= route_options,
                multi=True,
            ),

            html.Div([
                dcc.Input(id='input-1-state', type='text', placeholder='AE Name', style={'text-align': 'center'}, value=''),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    min_date_allowed = metro3.VALIDATION_DATE.min(),
                    max_date_allowed = metro3.VALIDATION_DATE.max(),
                    start_date = metro3.VALIDATION_DATE.min(),
                    end_date = metro3.VALIDATION_DATE.max(),
                    number_of_months_shown = 6,
                    day_size = 30,
                    initial_visible_month = metro3.VALIDATION_DATE.min(),
                    display_format = 'DD/MM/YY',
                    clearable = True,
                    start_date_placeholder_text= 'Select a date',
                    end_date_placeholder_text='Select a date'
                ),
                html.Button(id='submit-button', n_clicks=0, children='Submit')
            ]),

            dcc.RangeSlider(
                id='date_slider',
                min = 0,
                max = date_list.index.max(),
                value = [0, date_list.index.max()],
                marks = getMarks(),
                #updatemode = 'drag',
                allowCross = False,
            ),

            html.Div('', style={'padding': 10}),

            

            dcc.Graph(
                id='metro_density',
            ),

            

            

            html.Pre(id = 'range_text', style={'padding': 10}),





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

    html.Div(id='datesList', style={'display': 'none'}, children = ''),
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
'''
@app.callback(
    [Output('date-picker-range', 'start_date'), Output('date-picker-range', 'end_date')],
    [Input('date_slider', 'value')])
def update_start_date(value):
    return date_list[value[0]], date_list[value[1]]


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
@app.callback(
    [Output('date_slider', 'min'), Output('date_slider','max'), Output('date_slider', 'value')],
    [Input('route_filter', 'value'), Input('route_filter', 'options')])
def filter_routes(route_value, route_options):
    print("filter updated")
    print(route_value)

    global filterOne
    global filterTwo
    global date_list
    

    if ((route_value is None) | (route_value == [])):
        filterTwo = filterOne
    else:
        print(filterTwo.head())
        filterTwo = filterOne[filterOne['ROUTE_CODE'].isin(route_value)]
    
    date_list = pd.Series(filterTwo.VALIDATION_DATE.unique())

    return 0, date_list.index.max(), [0, date_list.index.max()]

@app.callback(
    Output('range_text', 'children'),
    [Input('date_slider', 'value')])
def print_slider_range(value):
    return str(date_list[value[0]].date()) + " " + str(date_list[value[1]].date())

@app.callback(
    Output('metro_density', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('date_slider', 'value')])
def filter_time_draw_figure(n_clicks, value):
    global filterTwo
    global filterThree
    global filterFour
    global date_list

    date_list = pd.Series(date_list)

    oneDay = pd.Timedelta(days=1)

    filterThree = filterTwo[(filterTwo['VALIDATION_DATE'] > (date_list[value[0]] - oneDay)) & (filterTwo['VALIDATION_DATE'] < (date_list[value[1]] + oneDay))]

    df = filterThree.groupby('stop_id').sum()[['USAGE']].reset_index()
    df = pd.merge(df, stopList, how="left", on="stop_id")

    filterFour = df

    site_lat = df.stop_lat
    site_lon = df.stop_lon
    usage = df.USAGE
    locations_name = df.stop_name
    stop_ids = df.stop_id
    hover = locations_name + " | Usage: " + usage.astype(str)

    t1 = go.Densitymapbox(
            lat = site_lat,
            lon = site_lon,
            z = usage,
            autocolorscale = False,
            colorscale = 'Viridis',
            #colorscale = colourscale,
            ###
            #colorbar = dict(
               # tick0 = 0,
              #  tickmode = 'array',
             #   tickvals = [0, 1000, 10000, 100000]
            #),
            radius = 20,
            meta = locations_name,
            text = locations_name,
            hoverinfo = 'text+z',
            name = "heatmap",
            zmin = 100,
            zmax = 200000,
        )

    t2 = go.Scattermapbox(
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
                    hovertext=hover,
                    hoverinfo = "text",
                    #hoverinfo="text",
                    
                    name="stops",
                )
    fig = {
                'data': [t1, t2],
                'layout': go.Layout(
                    title='Adelaide Stops',
                    autosize=False,
                    width = 900,
                    height = 800,
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
    global filterFour
    columns = [{"name": i, "id": i} for i in filterFour.columns]
    return columns, filterFour.to_dict('records')


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
    data = metro3[metro3['stop_id'] == clickData['points'][0]['meta']].copy()
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