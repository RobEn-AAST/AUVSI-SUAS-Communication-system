
import socket
from SSL import SSL_SERVER_WRAPPER

listen_addr = '127.0.0.1'
listen_port = 8082
server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'


ssl = SSL_SERVER_WRAPPER(certificate=server_cert,
                  key=server_key,
                  clients_certificates=client_certs)
bindsocket = socket.socket()
bindsocket.bind((listen_addr, listen_port))
bindsocket.listen(5)

print("Waiting for client")
newsocket, fromaddr = bindsocket.accept()
print("Client connected: {}:{}".format(fromaddr[0], fromaddr[1]))
conn = ssl.Initiate_Secure_Connection(newsocket)
print("SSL established. Peer: {}".format(conn.getpeercert()))
buf = b''  # Buffer to hold received client data
try:
    while True:
        data = conn.recv(4096)
        if data:
            # Client sent us data. Append to buffer
            buf += data
        else:
            # No more data from client. Show buffer and close connection.
            print("Received:", buf)
            break
finally:
    print("Closing connection")
    try:
        conn.shutdown(socket.SHUT_RDWR)
    except (socket.error, OSError, ValueError):
        pass
    conn.close()