import paho.mqtt.client as mqtt
import json
import threading
import time

class ChatClient:
    def __init__(self, broker='broker.hivemq.com', port=1883, on_message=None):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_mqtt_message
        
        self.username = None
        self.on_message_callback = on_message # Callback(msg)
        self.connected = False
        
        # Topics
        self.base_topic = "launcher/chat"
        
    def connect(self, username):
        try:
            self.username = username
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            self.connected = True
            
            # Announce login
            self.send_status_update(None)
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribe to my personal channel and global/discovery
        client.subscribe(f"{self.base_topic}/{self.username}")
        client.subscribe(f"{self.base_topic}/global")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            if self.on_message_callback:
                self.on_message_callback(payload)
        except Exception as e:
            print(f"Error parsing message: {e}")

    def send(self, topic, msg):
        if self.connected:
            self.client.publish(topic, json.dumps(msg))

    def send_message(self, target, content):
        # Send to target's topic
        msg = {"type": "message", "from": self.username, "content": content}
        self.send(f"{self.base_topic}/{target}", msg)

    def update_status(self, game_name):
        self.send_status_update(game_name)
        
    def send_status_update(self, game_name):
        # Broadcast status to global so friends can see (simplified discovery)
        # In a real app, we'd only send to friends, but for "serverless" we broadcast presence
        msg = {
            "type": "presence", 
            "username": self.username, 
            "status": "Online", 
            "game": game_name
        }
        self.send(f"{self.base_topic}/global", msg)

    def send_friend_request(self, target):
        msg = {"type": "new_request", "from": self.username}
        self.send(f"{self.base_topic}/{target}", msg)
        
    def accept_friend_request(self, requester):
        # Notify requester
        msg = {"type": "request_accepted", "from": self.username}
        self.send(f"{self.base_topic}/{requester}", msg)
        
        # Also send my status back to them immediately
        self.send_status_update(None)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
