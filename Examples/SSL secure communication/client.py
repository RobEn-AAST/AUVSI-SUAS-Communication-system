import socket
from SSL import SSL_CLIENT_WRAPPER

host_addr = '127.0.0.1'
host_port = 8082
server_sni_hostname = 'Safty'
server_cert = 'server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

ssl = SSL_CLIENT_WRAPPER(certificate=client_cert,
                  key=client_key,
                  server_certificate=server_cert,
                  hostname=server_sni_hostname)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn = ssl.Initiate_Secure_Connection(s)
conn.connect((host_addr, host_port))
print("SSL established. Peer: {}".format(conn.getpeercert()))
print("Sending: 'Hello, world!")
conn.send(b"Hello, world!")
print("Closing connection")
conn.close()