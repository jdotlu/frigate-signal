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
    event_after = event["after"]
    
    if event["type"] == "end" and event_after["has_clip"] and not event_after["false_positive"]:
        camera_name = event_after["camera"]
        event_id = event_after["id"]
        event_time = str(datetime.datetime.fromtimestamp(event_after["end_time"]))

        now = str(datetime.datetime.now())
        print(f"{now} Received {camera_name} event {event_id}")

        thumbnail_response = requests.get(f"http://frigate:5000/api/events/{event_id}/thumbnail.jpg")
        
        if (thumbnail_response.status_code == 200):
            thumbnail = thumbnail_response.content
            thumbnail64 = base64.b64encode(thumbnail).decode("ascii")

            signal_request_body = {"message": f"{camera_name}\n{event_time}UTC", "base64_attachments": [thumbnail64], "number": signal_number, "recipients": [signal_recipient]}
            signal_response = requests.post("http://signalapi:8080/v2/send", json = signal_request_body)
        else:
            event_string = str(event)
            print(f"Could not get thumbnail. Event = {event_string}")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("mqtt", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()
