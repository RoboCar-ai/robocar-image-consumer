from paho.mqtt.client import Client
from os import environ, path
from models.image_pb2 import Image as ImageModel
import json

BROKER_HOST = environ.get('BROKER_HOST')
IMAGE_TELEMETRY_TOPIC = 'robocars/{}/image-telemetry'.format(environ.get('CLIENT_ID'))
ROBOCAR_STATE_TOPIC = 'robocars/{}/status'.format(environ.get('CLIENT_ID'))
ROBOCAR_LWT_TOPIC = 'robocars/{}/lwt'.format(environ.get('CLIENT_ID'))

DATA_DIRECTORY = '/data/data'
SESSIONS_DIRECTORY = 'sessions'
SESSIONS_DIRECTORY_PATH = path.join(DATA_DIRECTORY, SESSIONS_DIRECTORY)
SESSIONS_FILE_PATH = path.join(SESSIONS_DIRECTORY_PATH, 'sessions.json')
STATE_FILE_PATH = path.join(SESSIONS_DIRECTORY_PATH, 'state.json')


def state_handler(client, userdata, msg):
    message = json.loads(msg.payload.decode('utf8'))

    connection_status = message['connectionStatus']

    with open(STATE_FILE_PATH, 'r') as f:
        state = json.loads(f.read())

    state['connectionStatus'] = connection_status

    with open (STATE_FILE_PATH, 'w') as f:
        f.write(json.dumps(state))
        

def image_telemetry_handler(client, userdata, msg):
    with open(SESSIONS_FILE_PATH, 'r') as f:
        session = json.loads(f.read())

    name = session['name']
    count = session['count']

    image = ImageModel()
    image.ParseFromString(msg.payload)
    dir = path.join(SESSIONS_DIRECTORY_PATH, name, str(count))
    image_path = path.join(dir, image.name)
    json_path = path.join(dir, 'record_{}.json'.format(int(image.telemetry.image_id)))
    with open(image_path, 'wb') as f:
        f.write(image.data)

    tele = {
        'user/angle': image.telemetry.steering_angle,
        'user/throttle': image.telemetry.throttle,
        'cam/image_array': image.name,
        'user/mode': image.telemetry.mode
    }

    with open(json_path, 'w') as f:
        f.write(json.dumps(tele))


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(IMAGE_TELEMETRY_TOPIC, 0)
    client.message_callback_add(IMAGE_TELEMETRY_TOPIC, image_telemetry_handler)
    client.subscribe(ROBOCAR_STATE_TOPIC, 0)
    client.message_callback_add(ROBOCAR_STATE_TOPIC, state_handler)


def init():
    if not path.exists(STATE_FILE_PATH):
        with open(STATE_FILE_PATH, 'w') as f:
            f.write('{"connectionStatus":"disconnected"}')


client = Client()
client.on_connect = on_connect

if __name__ == '__main__':
    init()
    print('Connecting to hub at:', BROKER_HOST)
    client.connect(BROKER_HOST)
    client.loop_forever()
