import paho.mqtt.client as mqtt
import base64
import requests
import json
import os
import datetime

signal_number = os.environ["SIGNAL_NUMBER"]
signal_recipient = os.environ["SIGNAL_RECIPIENT"]

print("Starting up...")

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("frigate/events")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    event = json.loads(msg.payload)
    
    if event["type"] == "end":
        camera_name = event["after"]["camera"]
        event_id = event["after"]["id"]
        event_time = str(datetime.datetime.fromtimestamp(event["after"]["end_time"]))

        now = str(datetime.datetime.now())
        print(f"{now} Received {camera_name} event {event_id}")

        thumbnail = requests.get(f"http://frigate:5000/api/events/{event_id}/thumbnail.jpg").content
        thumbnail64 = base64.b64encode(thumbnail).decode("ascii")

        signal_request_body = {"message": f"{camera_name} {event_time}UTC", "base64_attachments": [thumbnail64], "number": signal_number, "recipients": [signal_recipient]}
        signal_response = requests.post("http://signalapi:8080/v2/send", json = signal_request_body)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("mqtt", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()
