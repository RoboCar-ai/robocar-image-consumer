from paho.mqtt.client import Client
from os import environ

BROKER_HOST = environ.get('BROKER_HOST')
TOPIC = 'robocars/{}/image-telemetry'.format(environ.get('CLIENT_ID'))


def image_telemetry_handler(client, userdata, msg):
    print(msg.payload)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(TOPIC, 0)
    client.message_callback_add(TOPIC, image_telemetry_handler)


client = Client()
client.on_connect = on_connect

if __name__ == '__main__':
    print('Connecting to hub at:', BROKER_HOST)
    client.connect(BROKER_HOST)
    client.loop_forever()
