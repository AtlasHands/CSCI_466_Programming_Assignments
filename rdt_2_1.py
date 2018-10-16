import Network
import argparse
from time import sleep
import hashlib
import time

class Packet:
    ## the number of bytes used to store packet length
    seq_num_S_length = 10
    length_S_length = 10
    ## length of md5 checksum in hex
    checksum_length = 32 
    ack_length = 1
    nack_length = 1
        
    def __init__(self, seq_num, msg_S):
        self.seq_num = seq_num
        self.msg_S = msg_S
        
    @classmethod
    def from_byte_S(self, byte_S):
        if Packet.corrupt(byte_S):
            return "Corrupt"
        #extract the fields
        seq_num = int(byte_S[Packet.length_S_length : Packet.length_S_length+Packet.seq_num_S_length])
        msg_S = byte_S[Packet.length_S_length+Packet.seq_num_S_length+Packet.checksum_length+Packet.ack_length+Packet.nack_length:]
        return self(seq_num, msg_S)
    @staticmethod
    def isACK(response):
        if len(response) < 53:
            return False
        return str(1) == str(response[52])
    @staticmethod
    def isNACK(response):
        if len(response) < 54:
            return False
        return str(1) == str(response[53])
    def get_byte_S(self):#ack or nack passed as 0 or 1
        #convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        #convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(self.length_S_length)
        #compute the checksum
        checksum = hashlib.md5((length_S+seq_num_S+self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        #compile into a string
        return length_S + seq_num_S + checksum_S + self.msg_S
    def get_byte_S_Mod(self,ack,nack):
        #convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        #convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S) + self.ack_length + self.nack_length).zfill(self.length_S_length)
        #compute the checksum
        checksum = hashlib.md5((length_S+seq_num_S+self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        #compile into a string
        return length_S + seq_num_S + checksum_S + str(ack) + str(nack) + self.msg_S
    def getChecksum(self):
         #convert sequence number of a byte field of seq_num_S_length bytes
        seq_num_S = str(self.seq_num).zfill(self.seq_num_S_length)
        #convert length to a byte field of length_S_length bytes
        length_S = str(self.length_S_length + len(seq_num_S) + self.checksum_length + len(self.msg_S)).zfill(self.length_S_length)
        #compute the checksum
        checksum = hashlib.md5((length_S+seq_num_S+self.msg_S).encode('utf-8'))
        checksum_S = checksum.hexdigest()
        return checksum_S
    @staticmethod
    def get_msg_S(response):
        return response[10+10+34:]
    @staticmethod
    def corrupt(byte_S):
        #extract the fields
        length_S = byte_S[0:Packet.length_S_length]
        seq_num_S = byte_S[Packet.length_S_length : Packet.seq_num_S_length+Packet.seq_num_S_length]
        checksum_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length : Packet.seq_num_S_length+Packet.length_S_length+Packet.checksum_length]
        msg_S = byte_S[Packet.seq_num_S_length+Packet.seq_num_S_length+Packet.checksum_length+Packet.ack_length+Packet.nack_length :]
        #compute the checksum locally
        checksum = hashlib.md5(str(length_S+seq_num_S+msg_S).encode('utf-8'))
        computed_checksum_S = checksum.hexdigest()
        #and check if the same
        return checksum_S != computed_checksum_S
class RDT:
    ## latest sequence number used in a packet
    seq_num = 1
    ## buffer of bytes read from network
    byte_buffer = '' 
    recv_byte_buffer = ''
    def __init__(self, role_S, server_S, port):
        self.network = Network.NetworkLayer(role_S, server_S, port)
    
    def disconnect(self):
        self.network.disconnect()
        
    def rdt_1_0_send(self, msg_S):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S())
        
    def rdt_1_0_receive(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet
            #create packet from buffer content and add to return string
            if(Packet.corrupt(self.byte_buffer[0:length])):
                return "Corrupt"
            ret_S = p.msg_S if (ret_S is None) else ret_S + self.byte_buffer[length:]
            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration

    def rdt_1_0_receive_mod(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer = ''
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        while True:
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            if(p == "Corrupt"):
                return "Corrupt"
            #create packet from buffer content and add to return string
            ret_S = self.byte_buffer if (ret_S is None) else ret_S + self.byte_buffer
            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            #if this was the last packet, will return on the next iteration
    def rdt_1_0_receive_mod_withTimeout(self):
        ret_S = None
        byte_S = self.network.udt_receive()
        self.byte_buffer = ''
        self.byte_buffer += byte_S
        #keep extracting packets - if reordered, could get more than one
        while True:
            
            #check if we have received enough bytes
            if(len(self.byte_buffer) < Packet.length_S_length):
                return ret_S #not enough bytes to read packet length
            #extract length of packet
            length = int(self.byte_buffer[:Packet.length_S_length])
            if len(self.byte_buffer) < length:
                return ret_S #not enough bytes to read the whole packet
            p = Packet.from_byte_S(self.byte_buffer[0:length])
            if(p == "Corrupt"):
                return "Corrupt"
            #create packet from buffer content and add to return string
            ret_S = self.byte_buffer if (ret_S is None) else ret_S + self.byte_buffer
            #remove the packet bytes from the buffer
            self.byte_buffer = self.byte_buffer[length:]
            
            #if this was the last packet, will return on the next iteration
    def rdt_1_0_send_mod(self, msg_S,ack,nack):
        p = Packet(self.seq_num, msg_S)
        self.seq_num += 1
        self.network.udt_send(p.get_byte_S_Mod(ack,nack))
    def getResponse(self):#Gets response in sync
        msg_S = None
        while True:
            msg_S = self.rdt_1_0_receive_mod()
            if(not msg_S == None):
                break
        return msg_S#returns Valid return or returns "Corrupt"
    def getResponseWithTimeout(self):
        msg_S = None
        timeout = 4
        time_start = time.time()
        while True:
            if(time_start + timeout < time.time()):
                return "Timeout"
            msg_S = self.rdt_1_0_receive_mod_withTimeout()
            if(not msg_S == None):
                break
        return msg_S#returns Valid return or returns "Corrupt"
    def rdt_2_1_send(self, msg_S):
        while True:
            self.rdt_1_0_send_mod(msg_S,1,0) #Sending with rdt_1_0
            msg_R = self.getResponse() #Get Valid response
            if(msg_R == "Corrupt"):#if corrupt, print corrupt, try another send
                print("Corrupt")
            else:
                if(Packet.isACK(msg_R)):#If we receive and ACK
                    print("<<ACK RECEIVED")
                    break
                elif(Packet.isNACK(msg_R)):#Else its going to be a nack
                    print("<<NACK RECEIVED")
                    continue
                else:
                    print("Already got response")
                    break
    def rdt_2_1_receive(self):
        while True: #while we are getting Corrupt
            msg_S = self.getResponse()
            if(msg_S == "Corrupt"):
                print(">>NACK SENT")
                self.rdt_1_0_send_mod("",0,1)
            else:#When we get a good packet
                print(">>ACK SENT")
                self.rdt_1_0_send_mod("",1,0)#Send back an Ack
                return Packet.get_msg_S(msg_S)
        
    
    def rdt_3_0_send(self, msg_S):
        while True:
            sleep(.1)
            self.rdt_1_0_send_mod(msg_S,1,0) #Sending with rdt_1_0
            msg_R = self.getResponseWithTimeout() #Get Valid response
            if(msg_R == "Corrupt"):#if corrupt, print corrupt, try another send
                print("!!Corrupt!!")
            elif(msg_R == "Timeout"):
                print("!!Timeout!!")
            else:
                if(Packet.isACK(msg_R)):#If we receive and ACK
                    print("<<ACK RECEIVED")
                    break
                elif(Packet.isNACK(msg_R)):#Else its going to be a nack
                    print("<<NACK RECEIVED")
                    continue
                else:
                    print("Already got response")
                    break
        
    def rdt_3_0_receive(self):
        while True: #while we are getting Corrupt
            msg_S = self.getResponseWithTimeout()
            if(msg_S == "Corrupt"):
                print(">>NACK SENT")
                self.rdt_1_0_send_mod("",0,1)
            if(msg_S == "Timeout"):
                print("!!Timeout!!");
            else:#When we get a good packet
                print(">>ACK SENT")
                self.rdt_1_0_send_mod("",1,0)#Send back an Ack
                return Packet.get_msg_S(msg_S)
        

if __name__ == '__main__':
    parser =  argparse.ArgumentParser(description='RDT implementation.')
    parser.add_argument('role', help='Role is either client or server.', choices=['client', 'server'])
    parser.add_argument('server', help='Server.')
    parser.add_argdument('port', help='Port.', type=int)
    args = parser.parse_args()
    
    rdt = RDT(args.role, args.server, args.port)
    if args.role == 'client':
        rdt.rdt_1_0_send('MSG_FROM_CLIENT')
        sleep(2)
        print(rdt.rdt_1_0_receive())
        rdt.disconnect()
        
        
    else:
        sleep(1)
        print(rdt.rdt_1_0_receive())
        rdt.rdt_1_0_send('MSG_FROM_SERVER')
        rdt.disconnect()
        


        
        