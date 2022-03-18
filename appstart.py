import re
import sqlite3, os, json, ast
from flask import Flask, render_template, redirect
from flask_sqlalchemy import SQLAlchemy 
import dash
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

import paho.mqtt.client as mqtt

from mqtt import *

UPDATE_INTERVAL = 3000

con = sqlite3.connect('data.sqlite', check_same_thread=False)

'''
Stores MQTT record in table 'mqtt' in columns topic, value, timestamp
'''
def store_mqtt_record(con, topic, value, timestamp):
    try:
        con.cursor().execute(f'INSERT INTO mqtt (topic, value, timestamp) values (\'{topic}\', {value}, \'{timestamp}\');')
        con.commit()
    except sqlite3.Error as er:
        print(str(er))


'''
Create 'mqtt' table with id, topic, value, timestamp
'''
def gen_mqtt_tables(con):
    try:
        con.cursor().execute('CREATE TABLE mqtt (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, value FLOAT, timestamp DATETIME);')
        con.commit()
        print('CREATING TABLE MQTT')
    except sqlite3.Error as er:
        print(str(er))

def init_app():
    # Initialize flask and dash app
    appFlask = Flask(__name__)
    appDash = dash.Dash(__name__, server=appFlask, url_base_pathname='/dash/')

    # Generate mqtt table if does not exist
    gen_mqtt_tables(con)

    # Select first topic 
    SELECTED_TOPIC = topics[len(topics)-1][0]

    df_topic = pd.read_sql_query(f'SELECT * FROM mqtt WHERE topic=\'{SELECTED_TOPIC}\'', con)
    print(df_topic.head())

    fig_topic = px.line(df_topic, x='timestamp', y='value')


    appDash.layout = html.Div(children=[
    html.H1(children='Dash Application'),   
    html.Div(children='''
    Dash: Web Application
    '''),
    dcc.Graph(
        id='fig_topic',
        figure=fig_topic
    ), 
    dcc.Interval(
        id='update_interval',
        interval=UPDATE_INTERVAL,
        n_intervals=0
    ),
    dcc.Dropdown(list(map(lambda o: str(o[0]), topics)), SELECTED_TOPIC, id='topic_dropdown')
    ])

    @appDash.callback(
        Output('fig_topic', 'figure'), [Input('topic_dropdown', 'value'), Input('update_interval', 'n_intervals')]
    )
    def update_fig_topic(value, intervalVal):
        SELECTED_TOPIC = value
        print(f'selected topic: {SELECTED_TOPIC}')
        df_topic = pd.read_sql_query(f'SELECT * FROM mqtt WHERE topic=\'{SELECTED_TOPIC}\'', con)
        fig_topic = px.line(df_topic, x='timestamp', y='value')
        fig_topic['layout']['uirevision'] = 'uirevision'  
        
        return fig_topic

    return appFlask

app = init_app()

@app.route("/")
def home():
    """Landing page."""
    return render_template("index.jinja2", title="Landing Page")


if __name__ == "__main__":
    ## MQTT CLIENT ##
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(mqtt.error_string(rc) + ' Succesfully connected')
            client.subscribe(topics)
        else:
            print(mqtt.error_string(rc))

    def on_subscribe(client, userdata, mid, granted_qos):
        print("Subscribe " + str(userdata) + " mid: " + str(mid) + " qos: " + str(granted_qos))

    def on_message(client, userdata, msg):
        print("Topic: " + msg.topic + "=" + str(msg.payload.decode("utf-8")))
        val = str(msg.payload.decode("utf-8"))
        obj = ast.literal_eval(val)
        store_mqtt_record(con, msg.topic, str(obj['value']), str(obj['timestamp']))

    mqttc = mqtt.Client()
    
    # Flask spawns two instances while running on Debug Mode. MQTT needs to have ONLY ONE instance to work properly.
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        print("_________________________________________________________________________")
        print('MQTT START')
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        mqttc.on_subscribe = on_subscribe

        mqttc.connect(MQTT_URL, 1883, 60)
        mqttc.loop_start()
        print("_________________________________________________________________________")

    #####################

    app.run(host='0.0.0.0', port='5000', debug=True)
