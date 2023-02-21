from socket import *

if __name__ == '__main__':
    serverPort = 11000
    serverSocket = socket(AF_INET,SOCK_STREAM) ## LISTENING SOCKET
    serverSocket.bind(('',serverPort))
    serverSocket.listen(10)
    print('The server is ready to receive')
    while True:
        connectionSocket, addr = serverSocket.accept() ## RETURNS CONNECTION SOCKET
        message = connectionSocket.recv(2048) 
        capitalizedSentence = message.decode().upper()
        connectionSocket.send(capitalizedSentence.encode())
        print("server handled: " + str(addr) + " with message: " + message.decode())
        connectionSocket.close()
