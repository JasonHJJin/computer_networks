from socket import *

if __name__ == '__main__':
    serverName = 'localhost'
    serverPort = 12000
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    message = input('Input sentence: ')
    clientSocket.sendto(message.encode(),(serverName, serverPort))
    serverMessage, serverAddress = clientSocket.recvfrom(2048)
    print('Receive from server: ' + serverMessage.decode())
    clientSocket.close()
