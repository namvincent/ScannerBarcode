import json
import time
import paho.mqtt.client as mqtt

# Callback running on connection
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("mqtt/mes/wavesoldering")


# Callback running on new message
def on_message(client, userdata, msg):
    # We print each message received
    print(json.dump(mqtt.MQTTMessage,msg))
    print(msg.payload)
    if str(msg.payload) == "b'Ready to scan'":
          client.publish("mqtt/mes/wavesoldering", "Scanning")
    if str(msg.payload) == "b'Finish'":
        client.publish("mqtt/mes/wavesoldering", "Done")
        

# Initiate the MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Replace `<USER>`, `<PASSWORD>` and `<XXXXXX>.stackhero-network.com` with your server credentials.
client.username_pw_set("mesclient", "1")
client.connect("192.168.1.213", 1883, 60)

client.loop_forever()