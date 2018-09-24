import socket               
#Global Variables
htmlContents = None

#End Global Variables
#Game Settings
width = 10;
height = 10;
#End Game Settings
def resetGameBoard(name):
    html = open(name,"r")
    htmlData = html.read()
    htmlData = htmlData.replace("class=\"hit\"","")
    overwriteFile("index.html", htmlData)
def checkHit(x,y,referenceLines):
    if referenceLines[x][y] == "C":
        print("Hit!")
        return True
def updateGameBoard(x,y,type):
    global htmlContents
    htmlContents = htmlContents.replace("id=\"friendly-" + str(x) + "-"+ str(y) + "\"","id=\"friendly-" + str(x) + "-"+ str(y) + "\" class=\"" + type + "\"");
    overwriteFile("index.html",htmlContents)
def overwriteFile(name,data):
    file = open(name,"w")
    file.write(data)
    file.flush()
resetGameBoard("index.html")
board = open("own_board.txt","r")
boardContents = board.read()
html = open("index.html","r")
htmlContents = html.read()
print("Current Board Configuration:")
print(boardContents)
boardContents = boardContents.split("\n")
checkHit(0,4,boardContents)
s = socket.socket()
port = 12345
s.bind(('', port))
print("Socket bound to %s" %(port)) 
s.listen(5)
print("Socket listening...")     
while True:  
    c, addr = s.accept()
    print('Got connection from', addr)   
    c.send(('Connected to battleship').encode("UTF-8")) 
    data = c.recv(4096)
    print(data)
    coords = data.decode("UTF-8").split(",")
    x = int(float(coords[0]))
    y = int(float(coords[1]))
    if(checkHit(x,y,boardContents)):
        c.send(('Hit!').encode("UTF-8"))
        updateGameBoard(x,y,"hit")
    else:
        c.send(("Miss").encode("UTF-8"))
        updateGameBoard(x,y,"miss")
    c.close()
