import websocket
import json
import time
from threading import Thread
from mcww import shared
from mcww.utils import saveLogError
from mcww.comfy.comfyUtils import getWsComfyPathUrl


class Messages:
    def __init__(self):
        self._messages = list[dict]()
        self._ws = websocket.WebSocket()
        self._is_connected = False
        self._alive = True
        self._listen_thread = Thread(target=self._listenThreadInner, daemon=True)
        self._listen_thread.start()
        self._messageReceivedCallbacks = []


    def _connect(self):
        try:
            self._ws.connect(getWsComfyPathUrl(f"/ws?clientId={shared.clientID}"))
            self._is_connected = True
            print("WebSocket connected.")
        except Exception as e:
            print(f"Connection error: {e}")
            self._is_connected = False


    def _listenThreadInner(self):
        while self._alive:
            try:
                if self._is_connected:
                    out = self._ws.recv()
                    if out and isinstance(out, str):
                        message = json.loads(out)
                        self._messages.append(message)
                        for callback in self._messageReceivedCallbacks:
                            try:
                                callback(message)
                            except Exception as e:
                                saveLogError(e, "Error on executing a message received callback")
                else:
                    print("Attempting to reconnect...")
                    self._connect()
                    time.sleep(3)
            except websocket.WebSocketConnectionClosedException:
                print("WebSocket connection closed. Reconnecting...")
                self._is_connected = False
            except Exception as e:
                saveLogError(e, f"Error receiving ws message")
                self._is_connected = False


    def getLastMessage(self, message_type: str) -> dict | None:
        for message in reversed(self._messages):
            if message.get('type') == message_type:
                return message
        return None


    def close(self):
        self._alive = False
        self._ws.close()
        self._is_connected = False


    def addMessageReceivedCallback(self, callback):
        self._messageReceivedCallbacks.append(callback)

