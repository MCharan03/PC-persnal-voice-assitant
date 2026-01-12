import queue

class Bridge:
    def __init__(self):
        self.socketio = None
        self.screenshot_queue = queue.Queue()

    def set_socket(self, socketio_instance):
        self.socketio = socketio_instance

    def request_screenshot(self):
        if not self.socketio:
            return None
        
        print(">> [Bridge] Requesting Screenshot from Client...")
        self.socketio.emit('request_screenshot')
        
        try:
            # Wait up to 5 seconds for client to reply
            img_data = self.screenshot_queue.get(timeout=5)
            return img_data
        except queue.Empty:
            print(">> [Bridge] Screenshot timeout.")
            return None

    def receive_screenshot(self, img_data):
        self.screenshot_queue.put(img_data)

# Global Instance
server_bridge = Bridge()
