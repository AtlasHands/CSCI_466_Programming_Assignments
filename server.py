import socket
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import time
headers = ["Access-Control-Allow-Origin","*"]
hostName = ""
hostPort = int(float(sys.argv[1]))
board = open(sys.argv[2],"r")
boardContents = board.read()
boardContents = boardContents.split("\n")
#initializing the hitMap for the own board
ownBoardHitMap = [["_" for i in range(10)] for j in range(10)]
def hitMapToBytes(): #gets hit map as bytes
    global ownBoardHitMap
    tempChunks = []
    for i in range(10):
        tempVar = []
        for j in range(10):
            tempVar.append(ownBoardHitMap[i][j])
        tempJoin = "".join(tempVar)
        tempChunks.append(tempJoin)
    byteMap = bytes("\n".join(tempChunks),"utf-8")
    return byteMap
def boardContentsToBytes(): #getsboardContents as bytes
    global boardContents
    tempChunks = []
    for i in range(10):
        tempVar = []
        for j in range(10):
            tempVar.append(boardContents[i][j])
        tempJoin = "".join(tempVar)
        tempChunks.append(tempJoin)
    byteMap = bytes("\n".join(tempChunks),"utf-8")
    return byteMap
def isSunk(ship): #If ship is sunk returns true
    global ownBoardHitMap
    global boardContents
    for i in range(10):
        for j in range(10):
            if(boardContents[i][j] == ship):
                if(ownBoardHitMap[i][j] == "_"):
                    return False
    return True

def checkHit(x,y):#returns true if it is a hit
    global boardContents
    if boardContents[x][y] == "C" or boardContents[x][y] == "D" or boardContents[x][y] == "B" or boardContents[x][y] == "S" or boardContents[x][y] == "R":
        return True
def checkHitMap(x,y): #gets what is at x,y in hitmap
    global ownBoardHitMap
    location = ownBoardHitMap[x][y];
    return location
def updateBoardHitMap(x,y,update): #updates the hitmap
    global ownBoardHitMap
    ownBoardHitMap[x][y] = update;
def getQueryMessageAsKeyValues(path): #turns a query message into a keyValue pair array
        query = path.split("?")
        if(len(query) < 2):
            return None
        splitByPair = query[1].split("&")
        splitByKeyValue = []
        for i in range(len(splitByPair)):
            tempSplit = splitByPair[i].split("=")
            for j in range(len(tempSplit)):
                splitByKeyValue.append(tempSplit[j])
        return splitByKeyValue
def writeHeaders(request): #writes the default headers
        global headers
        i = 0
        while i < len(headers):
            request.send_header(headers[i],headers[i+1])
            i = i + 2
        request.end_headers()
class BattleShipServer(BaseHTTPRequestHandler): #handles HTTP requests
    #   GET is for clients geting the predi
    def do_GET(self):#handles GET requests
        print(self.client_address)
        if(self.path == "/api/getBoard"): #handles getboard returns hitmap
            self.send_response(200)
            writeHeaders(self)
            self.wfile.write(bytes("hitmap=","utf-8") + hitMapToBytes())
        elif(self.path == "/api/getPositions"):#gets boardContents
            data = bytes("positions=","utf-8") + boardContentsToBytes()
            self.send_response(200)
            writeHeaders(self)
            self.wfile.write(data)
        else: #This else serves regular files if they are requested and exist
            try:
                f = None

                if(self.path == "/"):
                    f=open("index.html","r")
                else:
                    i = 1;
                    path = []
                    while i < len(self.path):
                        path.append(self.path[i])
                        i = i+1
                    f = open("".join(path), 'r')
                self.send_response(200)
                writeHeaders(self)
                self.wfile.write(bytes(f.read(),"utf-8"))
                f.close()
            except FileNotFoundError:
                print("File not found")
                self.send_response(404)
                writeHeaders(self)
    #   POST is for submitting data.
    def do_POST(self): #handle POST requests
        query = getQueryMessageAsKeyValues(self.path)
        if(query[0] != "x" or query[2] != "y"):#handles incorrect format
            self.send_response(400)
            writeHeaders(self)
            self.wfile.write(bytes("<h1>Malformed request, example good: http://localhost?x=5&y=7</h1>","utf-8"))
        else:
            x = int(float(query[1]))#turning x and y to ints
            y = int(float(query[3]))
            global boardContents
            if(x>9 or y>9):#If x and y are out of bounds
                self.send_response(404)
                writeHeaders(self)
                return
            currentLocation = checkHitMap(x,y)
            if(currentLocation != "_"):#If its not _ its already been hit
                global ownBoardHitMap
                self.send_response(410)
                writeHeaders(self)
            else: #handle actual hits
                self.send_response(200)
                writeHeaders(self)
                if(checkHit(x,y)):
                    updateBoardHitMap(x,y,"H")
                    self.wfile.write(bytes("hit=1","utf-8"))
                    if(isSunk(boardContents[x][y])):
                        self.wfile.write(bytes("&sink=" + boardContents[x][y],"utf-8"))#handle sink
                else:#handle misses
                    self.wfile.write(bytes("miss=1","utf-8"))
                    updateBoardHitMap(x,y,"M")

myServer = ThreadingHTTPServer((hostName, hostPort), BattleShipServer)#initializing threaded server
print("Server started on " + str(hostPort))#telling the server has started
try:
    myServer.serve_forever() #serving!
except KeyboardInterrupt:
    pass

myServer.server_close()