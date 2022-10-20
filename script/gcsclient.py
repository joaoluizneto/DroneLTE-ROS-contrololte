import websocket, json
import threading, time

class GcsWebsocketClient:
    """
    GCS Client Interface

    """

    def __init__(self, api_url="ws://localhost:8000/ws/robot/zangado/", headers={'X-DroneApiKey':"hOgtypH7.eQM8nQbEUNyQY5gPUQg0IG1WbuopENfz"}):
        #websocket.enableTrace(True)
        ws = websocket.WebSocket()
        ws.connect(api_url,
					header=headers,
                    )
        self.ws = ws
        #self.ws.on_open = self.on_open
        #self.ws.run_forever()

    def send_telemetry(self, message=None):
        message = json.dumps({ 'type' : 'telemetry', 'message' : message })
        self.ws.send('%s' % message)


class GcsWebsocketReceiver:
    """
    GCS Client Interface

    """

    def __init__(self, api_url="ws://localhost:8000/ws/robot/zangado/", 
                    headers={'X-DroneApiKey':"hOgtypH7.eQM8nQbEUNyQY5gPUQg0IG1WbuopENfz"},
                    handlers=None ):

        if not handlers:
            self.handlers = {
                'arm' : print,
                'takeoff' : print
            }

        #websocket.enableTrace(True)

        ws = websocket.WebSocketApp(api_url,
                                    header=headers,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        self.ws = ws
        self.ws.on_open = self.on_open

        #self.wst = threading.Thread(target=self.ws.run_forever)
        #self.wst.daemon = True
        #self.wst.start()
        
    def on_message(self, ws, message):
        message = json.loads(message)
        #print(message['type'])
        if message['type']=='control':
            if message['message']['control_echo']:
                print(message)
            else:
                function_name = message['message']['command']['function']['name']
                function_params = message['message']['command']['function']['params']                    
                print(f'executing function {function_name}( {type(function_params)} {function_params})')
                if type(function_params) is dict:
                    result = self.handlers[function_name](**function_params)
                elif function_params is None:
                    result = self.handlers[function_name]()
                else:
                    result = self.handlers[function_name](function_params)

                message = json.dumps({ 'type' : 'control', 'message' : {'control_echo':True, 'result':result} })
                ws.send('%s' % message)
        return message

    def start_receiver(self, handlers=None):
        if not handlers:
            handlers=self.handlers
        else:
            self.handlers=handlers
        self.ws.run_forever()


    def on_error(self, ws, error):
        return error

    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")


    def on_open(self, ws):
        pass
