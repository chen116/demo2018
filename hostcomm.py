import socket
import time
class HostComm:
    def __init__(self,UDP_IP,UDP_PORT):
        self.UDP_IP=UDP_IP #"10.1.1.3"
        self.UDP_PORT=UDP_PORT #5000
        message = "udp started"
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    def send2host(self,message,target):
        if message < target:
            self.sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

    # tcp/ip
    # host = '10.1.1.3'
    # port = 5000

    # mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # mySocket.connect((host,port))

    # message = input(" -> ")

    # while message != 'q':
    #         a=(time.time())
    #         message+='ip'
    #         mySocket.send(message.encode())
    #         print(time.time()-a)
    #         data = mySocket.recv(1024).decode()

    #         print ('Received from server: ' + data)

    #         message = input(" -> ")

    # mySocket.close()
    # UDP
    # UDP_IP = "10.1.1.3"
    # UDP_PORT = 5000
    # message = "udp started"
    # sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    # sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

    # while message != 'q':
    #     print("sending:",message)
    #     message = input("->")
    #     sock.sendto(message.encode(), (UDP_IP, UDP_PORT))

if __name__ == '__main__':
    Main()
