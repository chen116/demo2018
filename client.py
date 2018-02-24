import socket
import time
def Main():
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
    UDP_IP = "10.1.1.3"
    UDP_PORT = 5005
    message = "udp started"
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    while message != 'q':
        sock.sendto(str(message), (UDP_IP, UDP_PORT))
        print("sending:",message)
        message = input("->")

if __name__ == '__main__':
    Main()
