import socket,sys
ip = sys.argv[1];
port = sys.argv[2];
x = sys.argv[3];
y = sys.argv[4];
print("Sending fire on " + x + "," + y + " to " + ip + ":" + port)
socket = socket.socket();
port = 12345

socket.connect((ip,port))
data = socket.recv(4096)
socket.send((x + "," + y).encode("UTF-8"))
hitData = socket.recv(4096)
print(hitData)