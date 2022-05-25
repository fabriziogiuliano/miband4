import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import pymongo
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

app = dash.Dash(__name__)
app.layout = html.Div(
    html.Div([
        html.H4('RSSI & HR DETECTION'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval=90*1000, # in milliseconds
            n_intervals=0
        )
    ])
)

@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))

def update_graph_live(n):
    for i in range(180):
        df2 = pd.DataFrame(columns=['DATETIME', 'DEV_ADDR', 'DEV_RSSI', 'HR'])
        config = {"host": "10.8.9.27", "token": "TFyCMKn7IOl0JhYUk1J0"}
        myclient = pymongo.MongoClient("mongodb://{}:27017/".format(config["host"]))
        mydb = myclient["BLE_scanner"]
        mycol = mydb["hr,rssi_detect"]
        x = mycol.find({}, {'_id': 0, 'DATETIME': 1, 'DEV_ADDR': 1,
                            'DEV_RSSI': 1, 'HR': 1}, sort=[('_id', pymongo.DESCENDING)])
        for data in x:
            df = pd.DataFrame.from_dict(data, orient='columns')
            df2 = pd.concat([df, df2], ignore_index=True)
        addr = list(np.unique(list(df2['DEV_ADDR'])))
        global l
        l = len(addr)
        date = df2['DATETIME']
        fig = make_subplots(
            rows=2, cols=1,
            vertical_spacing=0.3,
            specs=[[{"type": "scatter"}],
                   [{"type": "scatter"}]]
        )

        colors = ['red', 'green', 'black', 'royalblue','firebrick','yellow','purple','blue']

        for i in range(0,l):
            fig.add_trace(go.Scatter(x=df2[df2['DEV_ADDR']==addr[i]]['DATETIME'], y=df2[df2['DEV_ADDR']==addr[i]]['DEV_RSSI'],
                                     mode='lines+markers',
                                     name='RSSI {}'.format(addr[i]),line=dict(color=colors[i])
                                     ), row =1, col = 1
                          )
            fig.add_trace(go.Scatter(x=df2[df2['DEV_ADDR']==addr[i]]['DATETIME'], y=df2[df2['DEV_ADDR'] == addr[i]]['HR'],
                                     mode='lines+markers',
                                     name='HR {}'.format(addr[i]),  line=dict(color=colors[i])
                                     ), row=2, col=1
                          )
            fig.update_xaxes(title_text="time", row=1, col=1)
            fig.update_yaxes(title_text="RSSI", row=1, col=1)
            fig.update_xaxes(title_text="time", row=2, col=1)
            fig.update_yaxes(title_text="HR", row=2, col=1)
            fig.update_layout(height=900, width=1600)

        return fig


if __name__ == "__main__":
    app.run_server(debug=True)