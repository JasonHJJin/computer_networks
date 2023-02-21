from socket import socket, AF_INET, SOCK_STREAM
import select
import sys


class Proxy:
    def __init__(self, soc, tserver, fake_ip, server_ip):
        print('Init: Accepting client...')
        self.client, _ = soc.accept()
        self.servertb = tserver
        self.request_url = server_ip
        self.fake_ip = (fake_ip, 0)
        self.send_count, self.recv_count = 0, 0

    def run(self):
        request = self.getRequestFromClient()
        if request:
            self.connectServer(request)

    def connectServer(self, request):
        # self.servertb=socket(AF_INET,SOCK_STREAM)
        # self.servertb.bind(self.fake_ip)
        self.servertb.connect((self.request_url, 8080))
        self.servertb.send(request)
        self.communicate()
        self.servertb.close()

    def getRequestFromClient(self):
        request = (self.client.recv(4096).decode().split('\n')[0]+'\n').encode()
        if request is None:
            return None
        print(request)
        return request

    def communicate(self):
        inputs = [self.client, self.servertb]
        buff_size = 4096
        i = True
        while True and i:
            readable, writeable, errs = select.select(inputs, [], inputs, 20)
            if errs:
                break

            for soc in readable:
                data = soc.recv(buff_size)
                if data:
                    if soc is self.client:
                        self.send_count += 1
                        self.servertb.send(data)
                    if soc is self.servertb:
                        self.client.send(data)
                else:
                    i = False
                    break


        # self.client.close()
        # self.servertb.close()
if __name__ == '__main__':
    listen_port = sys.argv[1]
    fake_ip = sys.argv[2]
    server_ip = sys.argv[3]
    # servertb = socket(AF_INET, SOCK_STREAM)
    # servertb.bind((fake_ip,0))
    # servertb.connect((server_ip, 8080))
    pS = socket(AF_INET, SOCK_STREAM)
    pS.bind(('', int(listen_port)))
    pS.listen(1)
    print(sys.argv)
    print('Proxy receiving')
    while True:
        try:
            servertb = socket(AF_INET, SOCK_STREAM)
            servertb.bind((fake_ip, 0))
            Proxy(pS, servertb, fake_ip, server_ip).run()
        except Exception as e:
            print(e)
# except Exception:
# pS.client.close()
# pS.servertb.close()
