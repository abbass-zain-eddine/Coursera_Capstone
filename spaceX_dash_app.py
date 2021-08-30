# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
options=[{'label':'All','value':'All'}] + [{'label':i,'value':i} for i in spacex_df['Launch Site'].unique()  ]
marks={str(i*1000):j for i,j in enumerate(range(0,10001,1000))}
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',options=options,
                                value='All',placeholder='Select a Launch Site here',searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0,max=10000,step=1000,value=[0,10000],marks=marks),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
        Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'),
)

def Update_pie_chart(site):
    if site == 'All':
        pie_chart_data=spacex_df.groupby(spacex_df['Launch Site'])['class'].mean().reset_index(name='Rate')
        fig_pie=px.pie(data_frame=pie_chart_data,names='Launch Site',
        values='Rate',title='Total Success Launches by Site')

    else:
        pie_chart_data=spacex_df[spacex_df['Launch Site']==site]
        pie_chart_series=pie_chart_data['class'].value_counts()
        pie_chart_data=pd.DataFrame([pie_chart_series.index,pie_chart_series]).transpose()
        pie_chart_data.columns=['class','value']
        fig_pie=px.pie(data_frame=pie_chart_data,names='class',
        values='value',title='Total Success Launches for Site '+site)

    return fig_pie
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id="payload-slider", component_property="value")]
)

def Update_Scatter_chart(site,payload):
    values=[i for i in payload]
    if site == 'All':
        scatter_data=spacex_df[['Booster Version Category','Payload Mass (kg)','class']]
        scatter_data=scatter_data[(spacex_df['Payload Mass (kg)']>=values[0]) & 
        (spacex_df['Payload Mass (kg)']<=values[1])]
        fig_scatter=px.scatter(data_frame=scatter_data,x='Payload Mass (kg)',
        y='class',title='Correlation Between Payload and Success for all Sites',
        color='Booster Version Category')
    else:
        
        scatter_data=spacex_df[(spacex_df['Launch Site']==site) & 
        (spacex_df['Payload Mass (kg)']>=values[0]) & 
        (spacex_df['Payload Mass (kg)']<=values[1])]
        scatter_data=scatter_data[['Booster Version Category','Payload Mass (kg)','class']]
        fig_scatter=px.scatter(data_frame=scatter_data,x='Payload Mass (kg)',
        y='class',title='Correlation Between Payload and Success for Sites '+ site,
        color='Booster Version Category')

    return fig_scatter

# Run the app
if __name__ == '__main__':
    app.run_server()
