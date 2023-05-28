#Using TCP proxy allows you to forward traffic to bounce from host to host. This is a substitution to Wireshark. The proxy has a few parts
# we need to display the communication  between the local and remote machines to the console hexdump. We need to receive data from an imcoming socket 
# from either the local or remote machine. We need to manage the traffic direction between remote and local machines. And finnaly we setup a listening socket and pass it to our proxy_handler.


import sys
import socket
import threading

HEX_FILTER = ''.join([(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])

        printable = word.translate(HEX_FILTER)
        hexa = ''.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        results.append(f'{i:04x}    {hexa:<{hexwidth}}  {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results
def receive_from(connection):
    buffer = b""
    connection.settimeout(5) #Set a default timer for 5 sec, might be aggressive if you proxy out traffic
    try:
        while True:
            data = connection.recv(4096) # setup a loop to read response data into the buffer until there is no more data or we time out.
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

#sometimes you want to modify the response or request packets before the proxy sends them on their way.
def request_handler(buffer):
    # perform packet modifications
    return buffer
def response_handler(buffer):
    # perform packet modifications
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first): # Connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first: # ftp sends a banner first, this is to ensure that we make sure that we dont need to initate a connection to the remote side first and request data.
        remote_buffer = receive_from(remote_socket) # This accepts a connection socket object and performs a receive. We dump the contents of the packet so that we can inspect it.
        hexdump(remote_buffer)

    remote_buffer  = response_handler(remote_buffer) #send the received buffer to our local client, the rest of the codes purpose is to read form local client, process the data and send it to remote client.
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)
    
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line =  "[<==] Sending %d bytes to localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer): # no data left we close the remote and local socket.
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connection.")
            break
def server_loop(local_host, local_port, remote_host, remote_port, receive_first): # creates a socket and binds to a local host and listen
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit()

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True: # when a new connection arrives we hand it over to proxy_handler
        client_socket, addr = server.accept()
        # print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        #start a thread to talk to the remote host
        proxy_thread = threading.Thread(target = proxy_handler, args = (client_socket, remote_host, remote_port, receive_first)) # does the grunt work and receives the data stream.
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit()
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__== '__main__':
    main()




