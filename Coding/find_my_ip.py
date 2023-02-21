import socket

my_ip = socket.gethostbyname(socket.gethostname())
print(my_ip)