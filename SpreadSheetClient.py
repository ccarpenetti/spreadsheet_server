import socket
import json
import time
import requests
import sys

# Client stub for RPC communications
class SpreadSheetClient:

    def __init__(self, project_name):

        self.project_name = project_name

        # Find spreadsheet server
        self.host, self.port = self._find_server()
        if not self.host and not self.port:
            print("Client: there is no project under that name, timeout")
            sys.exit()

        # Connect to socket
        if not (self._connect_to_socket()):
            print("Client: cannot connect to server, timeout")
            sys.exit()

    def _find_server(self):

        # Go through all valid services, but get the service that was most recently updated
        i = 1

        print("Finding service ...")

        while i < 5:
        
            # Get response from name server
            response = requests.get('http://catalog.cse.nd.edu:9097/query.json')
            if response.status_code == 200:
                servers = response.json()

            s_list = [s for s in servers if s.get('type') == "spreadsheet" and s.get('project') == self.project_name]

            # If there are no servers under that name, wait and try again
            if len(s_list) == 0:
                time.sleep(i)
                i = i * 2
            else: # Find the most recent server
                server = max(s_list, key=lambda x: x['lastheardfrom'])
                return server['name'], int(server['port'])

        return None, None

    def _connect_to_socket(self):

        i = 1

        # Create socket instance using TCP
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                # Connect to server 
                server_addr = (self.host, self.port)
                self.s.connect(server_addr)

                print(f'Connected to server on {self.host} on port {self.port}...')
                print()
                return True
            except ConnectionRefusedError: # Account for if connecting to server fails
                if i == 1: # Only print this message one time
                    print("Waiting to connect to server ... ")
                if i > 4: 
                    return False
                time.sleep(i)
                i = i * 2

    def _send_req(self, request):

        i = 0
        
        # Prepare request
        request = json.dumps(request).encode('utf-8')

        while True:
            
            try:
                # Send data
                self.s.sendall(request)
                return True
            except:
                print(f'Waiting to send request...')
                return self._reconnect()

    def _get_resp(self):

        while True:
            try:
            # Receive response from server
                response = b""
                while True:
                    data = self.s.recv(1024)
                    if not data:
                        break
                    response += data
                    if b"\n" in response:
                        break
                response = json.loads(response.decode('utf-8').strip())
                return response['message']
            except:
                print('Waiting to receive response...')
                return self._reconnect()

    def _reconnect(self):

        old_port = self.port
        old_host = self.host
        i = 1
            
        self.s.close()  # Close the current socket
      
        # Find a new server option 
        while i < 5: 
            self.host, self.port = self._find_server()
            time.sleep(i)
            i = i * 2

        if old_port == self.port and old_host == self.host: # if we fail to find a new port and host
            return False

        if not self.host or not self.port:
            return False
        
        if not (self._connect_to_socket()):
            return False 

        return True # We have successfully reconnected

    def insert(self, row, col, value):
    
        # Craft json request for insert
        request = {"method": "insert", "row": row, "col": col, "value": value}

        # Send request and get response
        if not self._send_req(request):
            print("Client could not send request - timeout")
            sys.exit()
        response = self._get_resp()
        if response == False:
            print("Client could not get response - timeout")
            sys.exit()
        elif response == True: # If we can reconnect, resend original request and get new response
            self.insert(row, col, value)
        else: # If initial response worked the first time
            print(response)

    def lookup(self, row, col):
        
        # Craft json request for lookup
        request = {"method": "lookup", "row": row, "col": col}
       
        # Send request and get response
        if not self._send_req(request):
            print("Client could not send request - timeout")
            sys.exit()
        response = self._get_resp()
        if response == False:
            print("Client could not get response - timeout")
            sys.exit()
        elif isinstance(response, bool) and response == True: # If initial response failed, but we reconnected, retry
            self.lookup(row, col)
        else: # If initial response worked
            print(response)

    def remove(self, row, col):

        # Craft json request for remove
        request = {"method": "remove", "row": row, "col": col}

        # Send request and get response
        if not self._send_req(request):
            print("Client could not send request - timeout")
            sys.exit()
        response = self._get_resp()
        if response == False:
            print("Client could not get response - timeout")
            sys.exit()
        elif response == True: # If initial response failed, but we reconnected, resend original request and get new response
            self.remove(row, col)
        else: # If initial response worked the first time
            print(response)

    def size(self):
        
        # Craft json request for size
        request = {"method": "size"}
        
        # Send request and get response
        if not self._send_req(request):
            print("Client could not send request - timeout")
            sys.exit()
        response = self._get_resp()
        if response == False:
            print("Client could not get response - timeout")
            sys.exit()
        elif isinstance(response, bool) and response == True: # If initial response failed, but we reconnected, retry
            self.size()
        else: # If initial response worked
            print(response)

    def query(self, row, col, width, height):

        # Craft json request for query
        request = {"method": "query", "row": row, "col": col, "width": width, "height": height}
        
        # Send request and get response
        if not self._send_req(request):
            print("Client could not send request - timeout")
            sys.exit()
        response = self._get_resp()
        if response == False:
            print("Client could not get response - timeout")
            sys.exit()
        elif isinstance(response, bool) and response == True: # If initial response failed, but we reconnected, retry
            self.query(row, col, width, height)
        else: # If response worked the first time
            print(response)
