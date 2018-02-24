import socket
 
def Main():
    # tcp/ip
    # host = "10.1.1.3"
    # port = 5000
     
    # mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # mySocket.bind((host,port))
     
    # mySocket.listen(1)
    # conn, addr = mySocket.accept()
    # while True:
    #         data = conn.recv(1024).decode()
    #         if not data:
    #                 break
    #         print ("from connected  user: " + str(data))
             
    #         data = str(data).upper()
    #         print ("sending: " + str(data))
    #         conn.send(data.encode())
             
    # conn.close()
    #UDP
    UDP_IP = "10.1.1.3"
    UDP_PORT = 5005 
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT)) 
    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        print("received message:", data)    
     
if __name__ == '__main__':
    Main()
