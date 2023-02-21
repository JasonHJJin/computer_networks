#!/usr/bin/env python3.10
from email import message
import socket
import threading
from sys import argv
import select

# Declaring input parameters
listen_port = argv[1]
fake_ip = argv[2]
server_ip = argv[3]

servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servsock.bind(('', int(listen_port)))


def client_to_serv(conn):
    request = (conn.recv(4096).decode().split('\n')[0] + "\n").encode()
    if request is None:
        return None
    print("[Request Initiated]: " + request.decode())
    return request


def communicate(conn, sockserv):
    inputs = [conn, sockserv]
    outputs = []
    buff_size = 4096
    flag = True
    while flag:
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        if exceptional:
            break
        for soc_item in readable:
            message = soc_item.recv(buff_size)
            if message:
                if soc_item is conn:
                    print("[Client -> Proxy -> Server]: " + message.decode(), end="")
                    sockserv.send(message)
                if soc_item is sockserv:
                    print("[Server -> Proxy -> Client]: " + message.decode(), end="")
                    conn.send(message)
            else:
                flag = False
                break


def start():
    servsock.listen(1)
    print(argv)
    print("[STARTING] PROXY is starting...")
    while True:
        try:
            sockserv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sockserv.bind((fake_ip, 0))
            conn, addr = servsock.accept()
            print(f"[NEW CONNECTION] {addr} connected.")
            request = client_to_serv(conn)
            if request:
                sockserv.connect((server_ip, 8080))
                sockserv.send(request)
                communicate(conn, sockserv)
                sockserv.close()
                conn.close()
            print(f"[WAITING FOR NEW CONNECTION] {addr} disconnected.")
        except Exception as e:
            print(e)


start()
