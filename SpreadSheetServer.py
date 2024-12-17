import socket
import os
import sys
import SpreadSheet
import json
import time
import threading
import selectors

# Globals
selector = selectors.DefaultSelector()
ss = SpreadSheet.SpreadSheet()

# Upon startup, and subsequently once per minute, server sends an update describing itself
def update_name_server(ss, port, project_name):

    while True:
    # Find size of spreadsheet at this moment
        if isinstance(ss.size(), str): # If ss.size() returns "There are no rows or columns in this table", make width = 0 and height = 0 
            width = 0
            height = 0
        else:
            width, height = ss.size()

        update = {"type" : "spreadsheet", "owner" : "ccarpene", "port" : port, "project" : project_name, "width" : width, "height" : height}

        try:
            catalog = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            catalog.sendto(json.dumps(update).encode("utf-8"), ("catalog.cse.nd.edu", 9097))
            catalog.close()
        except:
            print("Server: socket name server failed.")

        time.sleep(60)

def modify_spreadsheet(connection):
    
    with open('sheet.log', 'a+') as log:

        log_size = 0

        while True:

            result = ''

            # Wait for incoming messages
            try:
                data = connection.recv(1024)
            except:
                break

            if not data:
                break

            request = json.loads(data.decode('utf-8'))

            # See if we should truncate the log file (i.e. we have met our limit of storing 100 transactions)
            if log_size == 100:
                
                # Prep table for serialization
                new_table = {str(key): value for key, value in ss.table.items()}

                # Document current state of table in the new checkpoint 
                with open('newsheet.ckpt', 'w+') as new_check:
                    new_check.write(json.dumps(new_table))
                    new_check.flush()
                    os.fsync(new_check.fileno())

                # Rename old checkpoint to new checkpoint
                os.rename(new_check.name, 'sheet.ckpt')

                # Truncate the log
                log.truncate(0)
                log.seek(0)
                log_size = 0


            # If request asks to insert, insert into spreadsheet
            if request['method'] == 'insert':
            
                row = request['row']
                col = request['col']
                value = request['value']

                # Ensure that row and col numbers are integers
                if not (isinstance(row, int)) or not (isinstance(col, int)):
                    result = 'failure'
                    message = 'invalid inputs for row or col'
                elif row < 0 or col < 0:
                    result = 'failure'
                    message = 'invalid inputs for row or col'
                else:
                    # First collect the old value (for logging the transaction)
                    result, old_value = ss.lookup(row, col)
                    
                    # Add this transaction to the log file
                    if result:
                        transaction = {"method": request['method'], "row": request['row'], "col": request['col'], "old_value": old_value, "new_value": request['value'], "user": os.getlogin(), "time": time.gmtime(time.time())}
                        log.write(json.dumps(transaction) + '\n')
                        log.flush()
                        os.fsync(log.fileno())
                        log_size += 1

                    # Insert new value
                    if ss.insert(row, col, value):
                        result = 'success'
                        message = f'insert of {value} at ({row}, {col})'

            # Handle lookup request
            elif request['method'] == 'lookup':
                
                row = request['row']
                col = request['col']

                # Ensure that row and col numbers are integers
                if not (isinstance(row, int)) or not (isinstance(col, int)):
                    result = 'failure'
                    message = 'invalid inputs for row or col'
                elif row < 0 or col < 0:
                    result = 'failure'
                    message = 'invalid inputs for row or col'
                else:
                    result, message = ss.lookup(row, col)
                    result = 'success'

            # Handle remove request
            elif request['method'] == 'remove':
                
                row = request['row']
                col = request['col']

                # Ensure that row and col numbers are integers
                if not (isinstance(row, int)) or not (isinstance(col, int)):
                    result = 'failure'
                    message = 'invalid inputs for row or col'
                elif row < 0 or col < 0:
                    result = 'failure'
                    message = 'invalid inputs for row or col'
                else:
                    # First collect the original value (for logging the transaction)
                    result, old_value = ss.lookup(row, col)
                    
                    # Add this transaction to the log file
                    if result:
                        transaction = {"method": request['method'], "row": request['row'], "col": request['col'], "old_value": old_value, "new_value": None, "user": os.getlogin(), "time": time.gmtime(time.time())}
                        log.write(json.dumps(transaction) + '\n')
                        log.flush()
                        os.fsync(log.fileno())
                        log_size += 1

                    # Now remove value
                    if (ss.remove(row, col)):
                        result = 'success'
                        message = f'removed at key ({row}, {col})'
                    else:
                        result = 'success'
                        message = f'at ({row}, {col}), no value was found in spreadsheet, nothing to remove'

            # Handle size request
            elif request['method'] == 'size':
                result = 'success'
                message = f'{ss.size()}'
        
            # Handle query request 
            elif request['method'] == 'query':
                
                row = request['row']
                col = request['col']
                width = request['width']
                height = request['height']

                # Ensure that row and col numbers are integers
                if not (isinstance(row, int)) or not (isinstance(col, int)) or not (isinstance(width, int)) or not (isinstance(height, int)):  
                    result = 'failure'
                    message = 'invalid integer inputs for row, col, width, or height.'
                elif row < 0 or col < 0 or width <= 0 or height <= 0:
                    result = 'failure'
                    message = 'invalid integer inputs for row, col, width, or height.'
                else:
                    result = 'success'
                    message = ss.query(row, col, width, height)

            response = {"method": request['method'], "result": result, "message": message}

            connection.sendall((json.dumps(response) + '\n').encode('utf-8'))

def accept_connection(server_socket):

    # Accept connection
    try:
        connection, client_addr = server_socket.accept()
    except:
        print("Server: socket failed to connect.")
        sys.exit()

    connection.setblocking(False)
    selector.register(connection, selectors.EVENT_READ, modify_spreadsheet)

def main():
    # Create socket instance
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except:
        print("Server: socket initialization failed.")

    # Collect project name
    project_name = sys.argv[1]

    host = '0.0.0.0' # Destination of server
    port = 0
    server_addr = (host, port)

    # Bind to the socket
    try:
        server_socket.bind(server_addr)
    except:
        print(f"Server: socket failed to connect on {port}.")
        sys.exit()
        
    # Get new port number
    port = server_socket.getsockname()[1]

    print(f"Listening on port {port}... ")
    print()

    # Open checkpoint file and log file (if they exist)
    if os.path.exists('sheet.log'):
        log = open('sheet.log', 'r+')

        # Upon startup, read in checkpoint into table
        if os.path.exists('sheet.ckpt'):
            checkpoint = open('sheet.ckpt', 'r')
            line = checkpoint.readline()
            if line:
                old_dict = json.loads(line)

                # Convert string keys back into tuple keys
                for key, value in old_dict.items():
                    row, col = map(int, key.strip('()').split(', '))
                    ss.table[(row, col)] = value
        
            checkpoint.close()

        # Apply all changes stated in the log to the checkpoint file
        for transaction in log:
            transaction = json.loads(transaction)
            if transaction['method'] == 'insert':
                ss.insert(transaction['row'], transaction['col'], transaction['new_value'])
            elif transaction['method'] == 'remove':
                ss.remove(transaction['row'], transaction['col'])

        # Close the log
        log.close()
    
    # Once we have the port, start sending updates to the name server
    t1 = threading.Thread(target=update_name_server, args=(ss, port, project_name))
    t1.daemon = True # Allows for thread to exit once the main program is exited
    t1.start()

    # Listen for incoming requests
    server_socket.listen()      
    server_socket.setblocking(False)
    selector.register(server_socket, selectors.EVENT_READ, accept_connection)

    while True:

        clients = selector.select()

        # Event-driven server
        for key, mask in clients:
            callback = key.data
            callback(key.fileobj)

if __name__ == "__main__":
    main()
