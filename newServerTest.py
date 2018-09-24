import socket
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
import time
headers = ["Access-Control-Allow-Origin","*"]
hostName = "localhost"
hostPort = 80
board = open("own_board.txt","r")
boardContents = board.read()
boardContents = boardContents.split("\n")
#initializing the hitMap for the own board
ownBoardHitMap = [["_" for i in range(10)] for j in range(10)]
def initializeHitMap():
    global ownBoardHitMap
    for i in range(len(ownBoardHitMap)):
        ownBoardHitMap.append("_")
        for j in range(len(ownBoardHitMap[0])):
            ownBoardHitMap[i].append("_")
def hitMapToBytes():
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
initializeHitMap();
def checkHit(x,y):
    global boardContents
    if boardContents[x][y] == "C":
        return True
def print2dArray(array):
    for i in range(len(array)):
        for j in range(len(array[0])):
            print(array[i][j])
def checkHitMap(x,y):
    global ownBoardHitMap
    location = ownBoardHitMap[x][y];
    return location
def updateBoardHitMap(x,y,update):
    global ownBoardHitMap
    ownBoardHitMap[x][y] = update;
def getQueryMessageAsKeyValues(path):
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
def writeHeaders(request):
        global headers
        i = 0
        while i < len(headers):
            request.send_header(headers[i],headers[i+1])
            i = i + 2
        request.end_headers()
class BattleShipServer(BaseHTTPRequestHandler):
    #   GET is for clients geting the predi
    def do_GET(self):
        if(self.path == "/api/getBoard"):
            self.send_response(200)
            writeHeaders(self)
            self.wfile.write(bytes("hitmap=","utf-8") + hitMapToBytes())
        else:
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
    #   POST is for submitting data.
    def do_POST(self):
        query = getQueryMessageAsKeyValues(self.path)
        if(query[0] != "x" or query[2] != "y"):
            self.send_response(400)
            writeHeaders(self)
            self.wfile.write(bytes("<h1>Malformed request, example good: http://localhost?x=5&y=7</h1>","utf-8"))
        else:
            x = int(float(query[1]))
            y = int(float(query[3]))
            global boardContents
            currentLocation = checkHitMap(x,y)
            if(currentLocation != "_"):
                global ownBoardHitMap
                self.send_response(410)
                writeHeaders(self)
            else:
                self.send_response(200)
                writeHeaders(self)
                if(checkHit(x,y)):
                    self.wfile.write(bytes("hit=1","utf-8"))
                    updateBoardHitMap(x,y,"H")
                else:
                    self.wfile.write(bytes("miss=1","utf-8"))
                    updateBoardHitMap(x,y,"M")

myServer = ThreadingHTTPServer((hostName, hostPort), BattleShipServer)

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()