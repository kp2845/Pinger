import os
import select
import struct
import sys
import time
from socket import *

# Should use stdev
from statistics import stdev
ICMP_ECHO_REQUEST = 8
#timeRTT = []

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer



def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
   # packrec = 0 #define start

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start

        # Fetch the ICMP header from the IP packet
        ICMPheaderfetch = recPacket[20:28]
        Type, Code, Checksum, packetid, Sequence = struct.unpack('bbHHh', ICMPheaderfetch)
        if packetid == ID:
            recBytes = struct.calcsize('d')
            timesent = struct.unpack('d', recPacket[28:28 + recBytes])[0]
            #timeReceived.append(timeReceived - timesent)
            #packrec += 1
            return timeReceived - timesent
        else:
            return ['0, 0.0', '0', '0.0']
        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    #destAddr ='127.0.0.1' REMOVE

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)


    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str


    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,  	# the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    #print("Pinging " + dest + " using Python:")
    #print("")
    # Calculate vars values and return them
    #  vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]


    # Send ping requests to a server separated by approximately one second
    timeRTT = []
    for i in range(0,4):
        delay = doOnePing(dest, timeout)
        #print(delay)
        #print("Reply from " + dest + ": bytes=" + " time=" + str(round(delay, 2) *1000) + "ms" + " TTL=")
        #print(delay)
        time.sleep(1)  # one second
        timeRTT.append(delay)
        #print(delay)
    #print("")
    #print("---- google.co.il ping statistics ----")

    packet_min = min(timeRTT)
    packet_max = max(timeRTT)
    packet_avg = ((sum(timeRTT)) / 4)
    stdev_var = (timeRTT)
    vars = [str(packet_min), str(packet_avg), str(packet_max),str(stdev(stdev_var))]
    print(vars)
    return vars



if __name__ == '__main__':
    ping("google.co.il")
