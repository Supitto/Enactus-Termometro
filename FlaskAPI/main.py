import paho.mqtt.client as cliente
from flask import Flask
import json

def retrive_nested(dic,keys):
    var = dic[keys[0]]
    for i in keys[1:]:
        var = var[i]
    return var

def insert_nested(dic, keys, value): #got it on https://stackoverflow.com/questions/13687924/setting-a-value-in-a-nested-python-dictionary-given-a-list-of-indices-and-value
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value


def on_message(client, userdata, message):
    if str(message.topic)[:15] == "enactus/sensor/":
        print message.topic+" "+str(message.payload)
        insert_nested(LKV_DIC,str(message.topic)[15:].split('/'),str(message.payload))
    print LKV_DIC
def on_connect(client, userdata, flags, rc):
    client.subscribe("enactus/sensor/#")


API = Flask(__name__)

@API.route('/')
def baseSlash():
    return json.dumps({'code':200,'message':'Working Good'})

@API.route('/LKV/<device_name>/',defaults={'subnames': ''})
@API.route('/LKV/<device_name>/<path:subnames>')
def getLastKnowValue(device_name,subnames):
    try:
        value = retrive_nested(LKV_DIC[device_name],subnames.split('/'))
        return json.dumps({'code':200,'message':'Value found', 'Value' : value})
    except:
        return json.dumps({'code':404,'message':'Value not found'})

@API.route('/LKV/')
def getAllLastKnowValue():
    return json.dumps({'code':200,'message':'Value found', 'Value' : LKV_DIC})

@API.route('/ForceValue/<path:device_name>/<value>')
def forceValue(device_name,value):
    try:
        insert_nested(LKV_DIC,device_name.split('/'),value)
        return json.dumps({'code':200,'message':'Value replaced'})
    except:
        return json.dumps({'code':400,'message':'Bad Request'})

@API.route('/SetID/<id>')
def forceID(id):
    global client
    global ID
    id = ID
    client = cliente.Client(ID)
    client.on_message=on_message
    client.on_connect=on_connect
    client.connect("iot.eclipse.org")
    client.loop_start()
    return json.dumps({'code':200,'message':'ID changed'})
ID = "Test"
LKV_DIC = {}
client = cliente.Client()
forceID(ID)
API.run()