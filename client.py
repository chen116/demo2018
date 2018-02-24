import socket
import time
def Main():
        host = '10.1.1.3'
        port = 5000

        mySocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mySocket.connect((host,port))

        message = input(" -> ")

        while message != 'q':
                a=(time.time())
                message+='ip'
                mySocket.send(message.encode())
                print(time.time()-a)
                data = mySocket.recv(1024).decode()

                print ('Received from server: ' + data)

                message = input(" -> ")

        mySocket.close()

if __name__ == '__main__':
    Main()
