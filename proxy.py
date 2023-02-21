#!/usr/bin/env python3.10

import argparse
import socket
import threading
import select

def parse_arguments():
    parser = argparse.ArgumentParser(description='Start a proxy server.')
    parser.add_argument('listen_port', type=int, help='port on which to listen for incoming connections')
    parser.add_argument('fake_ip', type=str, help='fake IP address to use')
    parser.add_argument('server_ip', type=str, help='IP address of the server to forward requests to')
    return parser.parse_args()

def client_to_serv(conn):
    request = (conn.recv(4096).decode().split('\n')[0] + "\n").encode()
    if not request:
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

def handle_connection(servsock, fake_ip, server_ip):
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

def start_server():
    args = parse_arguments()
    servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servsock.bind(('', args.listen_port))
    servsock.listen(1)
    print(f"[STARTING] PROXY is starting on port {args.listen_port}...")
    while True:
        handle_connection(servsock, args.fake_ip, args.server_ip)

if __name__ == '__main__':
    start_server()
