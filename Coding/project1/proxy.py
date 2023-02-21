import sys
import socket
import select
import time
import argparse
import re

p = re.compile('/vod/\d+Seg\d+-Frag\d+')


class ForwardBrowser:
    def __init__(self):
        self.fbsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.fbsock.bind((args.fakeip, 0))
            self.fbsock.connect((host, port))
            return self.fbsock
        except Exception:
            return False


class ServProcess:
    def __init__(self, host, port):
        self.inputLog = []
        self.channel = {}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(200)

    def operation(self):
        self.inputLog.append(self.server)
        self.tput = 10
        self.avgtPut = 10
        self.bitrate = 10
        self.duration = 1
        self.chunkname = None
        contentlen = None
        startTime = None

        while True:
            readList, writeList, exceptionList = select.select(self.inputLog,[],[])
            for self.ind in readList:
                if self.ind == self.server:
                    self.createConn()
                    break
            
            if (self.ind.getpeername()[0] == args.serverip):
                self.data = self.ind.recv(4096)
                measureTime = time.time()
                if 'Content-Type: video' in self.data:
                    self.duration = measureTime - startTime
                    contentlen = float(self.data.split('\n')[3].rstrip().split(' ')[1])
                    self.tput = (contentlen * 8 / 1024) / self.duration
                    self.avgtPut = float(args.alpha) * self.tput + (1-float(args.alpha)) * self.avgtPut
                    self.bitrate = selectBitRate(self.avgtPut)
                    with open(args.logfile, 'w') as f:
                        f.write('%d %f %d %.1f %d %s %s\n' % (time.time(), self.duration, self.tput, self.avgtPut, self.bitrate, args.serverip, self.chunkname))
            
            else:
                self.data = self.ind.recv(4096)
                measureTime2 = time.time()
                if ('GET /vod/' in self.data):
                    startTime = measureTime2
            
            if len(self.data) == 0:
                print(self.ind.getpeername(), end="has disconnected")
                self.inputLog.remove(self.ind)
                self.inputLog.remove(self.channel[self.ind])
                self.channel[self.channel[self.ind]].close()
                self.channel[self.ind].close()
                del self.channel[self.channel[self.ind]]
                del self.channel[self.ind]
                break
            else:
                if (self.ind.getpeername()[0] == args.serverip):
                    if 'BigBuckBunny_6s.mpd' in self.data:
                        self.data = self.data.replace('BigBuckBunny_6s.mpd', 'BigBuckBunny_6s_nolist.mpd')
                        print('manifest file replaced')
                    self.channel[self.ind].send(self.data)
                    pass
                else:
                    if ('GET /vod/' in self.data):
                        tar = self.data.split()
                        if p.match(tar[1]):
                            temp = tar[1]
                            self.chunkname = choosechunk(self.bitrate, tar[1])
                            data = data.replace(tar[1], self.chunkname)
                            print("chunkname changed to" + self.chunkname)
                    self.channel[self.ind].send(data)
    
    def createConn(self):
        fbsock = ForwardBrowser().start(args.serverip, 8080)
        clientsock, clientaddr = self.server.accept()
        if fbsock:
            print(clientaddr, end="has connected")
            self.inputLog.append(clientsock)
            self.inputLog.append(fbsock)
            self.channel[fbsock] = clientsock
            self.channel[clientsock] = fbsock
        else:
            print("Cannot establish connection with remote server.")
            print(f"Closing connection with client side {clientaddr}")
            clientsock.close()

def choosechunk(bitrate, url):
    s = url.split('-')
    seg = s[0].find('Seg')
    frag = s[1].find('Frag')
    s = '/vod/' + str(bitrate) + 'Seg' + s[0][seg+3:] + '-Frag' + s[1][frag+4:]
    return s

def selectBitRate(avgtPut):
    print(avgtPut)
    if (avgtPut >= 1.5*1000):
        print("1000kbps")
        return 1000
    elif (avgtPut >= 1.5*500):
        print("500kbps")
        return 500
    elif (avgtPut >= 1.5*100):
        print("100kbps")
        return 100
    else:
        print("10kbps")
        return 10



def main():
    main_server = ServProcess('', int(args.port))
    try:
        main_server.operation()
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launch a proxy.')
    parser.add_argument('logfile', help='name of the logfile')
    parser.add_argument('alpha', help='alpha')
    parser.add_argument('port', help='Listening port')
    parser.add_argument('fakeip', help='Fake ip for proxy')
    parser.add_argument('serverip', help='server ip')
    args = parser.parse_args()
    main()