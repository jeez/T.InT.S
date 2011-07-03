import socket
import re
import osc

class Player:
    def __init__(self, id, lh, rh, ls, rs, torso, li, ri, head):
        self.id = id
        self.lh = lh
        self.rh = rh
        self.ls = ls
        self.rs = rs
        self.torso = torso
        self.li = li
        self.ri = ri
        self.head = head


def hasCollision(a, b):
    iA = int(float(a))
    iB = int(float(b))

    if iA in range(iB-105, iB+105):
        return True


def playersPartsAreColliding(partP1, partP2):
    if (hasCollision(partP1[1], partP2[1]) and hasCollision(partP1[2], partP2[2]) and hasCollision(partP1[3], partP2[3])):
        return True


UDP_IP="127.0.0.1"
UDP_PORT=50125

DELAY=15

sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP
sock.bind( (UDP_IP,UDP_PORT) )
regex = re.compile("([a-z][a-z])x([-.0-9]*)y([-.0-9]*)z([-.0-9]*)")

hasTwoPlayers = False
isDetecting = False

stateMemory = {"1h":0, "1s":0, "1t":0, "2h":0, "2s":0, "2t":0, "3h":0, "3s":0, "3t":0}
msgSentMemory = {"1h":False, "1s":False, "1t":False, "2h":False, "2s":False, "2t":False, "3h":False, "3s":False, "3t":False}

osc.init()

p1 = Player(-1, [], [], [], [], [], [], [], [])
p2 = Player(-1, [], [], [], [], [], [], [], [])

while True:
    data, addr = sock.recvfrom( 1024 ) # buffer size is 1024 bytes
    all = regex.findall(data)

    if (data[0] == "p"):
        if (all[0][1] == "-999.0" and all[0][2] == "-999.0" and all[0][3] == "-999.0" and all[1][1] == "-999.0" and all[1][2] == "-999.0" and all[1][3] == "-999.0"):
            #LOST TRACK
            msg = "LOST USER " + data[1]
            print msg
            hasTwoPlayers = False
            if (p1.id == data[1]):
                p1 = Player(-1, [], [], [], [], [], [], [], [])
                cmd = ["p1l"]
                osc.sendMsg("/titsPD", cmd, "127.0.0.1", 9999)
            elif (p2.id == data[1]):
                p2 = Player(-1, [], [], [], [], [], [], [], [])
                cmd = ["p2l"]
                osc.sendMsg("/titsPD", cmd, "127.0.0.1", 9999)
        else:
            if (p1.id == data[1]):
                p1 = Player(data[1], all[0], all[1], all[2], all[3], all[4], all[5], all[6], all[7])
            elif (p2.id == data[1]):
                p2 = Player(data[1], all[0], all[1], all[2], all[3], all[4], all[5], all[6], all[7])
            elif (p1.id == -1):
                p1 = Player(data[1], all[0], all[1], all[2], all[3], all[4], all[5], all[6], all[7])
                cmd = ["p1c"]
                osc.sendMsg("/titsPD", cmd, "127.0.0.1", 9999)
            elif (p2.id == -1):
                p2 = Player(data[1], all[0], all[1], all[2], all[3], all[4], all[5], all[6], all[7])
                cmd = ["p2c"]
                osc.sendMsg("/titsPD", cmd, "127.0.0.1", 9999)

        if (p1.id != -1 and p2.id != -1):
            hasTwoPlayers = True

    if hasTwoPlayers:
        isDetecting = False
        for k,v in stateMemory.iteritems():
            if stateMemory[k] > 0:
                stateMemory[k] -= 1

        # WARNING: DUMB/LAZY APPROACH AHEAD!!!!!!
        # ONE touching TWO
        if playersPartsAreColliding(p1.lh, p2.head) or playersPartsAreColliding(p1.rh, p2.head):
            if stateMemory["2h"] < DELAY:
                stateMemory["2h"] += 2
            isDetecting = True
        if playersPartsAreColliding(p1.lh, p2.ls) or playersPartsAreColliding(p1.lh, p2.rs) or playersPartsAreColliding(p1.rh, p2.ls) or playersPartsAreColliding(p1.rh, p2.rs):
            if stateMemory["2s"] < DELAY:
                stateMemory["2s"] += 2
            isDetecting = True
        if playersPartsAreColliding(p1.lh, p2.torso) or playersPartsAreColliding(p1.rh, p2.torso):
            if stateMemory["2t"] < DELAY:
                stateMemory["2t"] += 2
            isDetecting = True
        if playersPartsAreColliding(p1.lh, p2.li) or playersPartsAreColliding(p1.lh, p2.ri) or playersPartsAreColliding(p1.rh, p2.li) or playersPartsAreColliding(p1.rh, p2.ri):
            if stateMemory["2t"] < DELAY:
                stateMemory["2t"] += 2
            isDetecting = True

        # TWO touching ONE
        if playersPartsAreColliding(p2.lh, p1.head) or playersPartsAreColliding(p2.rh, p1.head):
            if stateMemory["1h"] < DELAY:
                stateMemory["1h"] += 2
            isDetecting = True
        if playersPartsAreColliding(p2.lh, p1.ls) or playersPartsAreColliding(p2.lh, p1.rs) or playersPartsAreColliding(p2.rh, p1.ls) or playersPartsAreColliding(p2.rh, p1.rs):
            if stateMemory["1s"] < DELAY:
                stateMemory["1s"] += 2
            isDetecting = True
        if playersPartsAreColliding(p2.lh, p1.torso) or playersPartsAreColliding(p2.rh, p1.torso):
            if stateMemory["1t"] < DELAY:
                stateMemory["1t"] += 2
            isDetecting = True
        if playersPartsAreColliding(p2.lh, p1.li) or playersPartsAreColliding(p2.lh, p1.ri) or playersPartsAreColliding(p2.rh, p1.li) or playersPartsAreColliding(p2.rh, p1.ri):
            if stateMemory["1t"] < DELAY:
                stateMemory["1t"] += 2
            isDetecting = True

        # TWO touching HIMSELF
        if playersPartsAreColliding(p2.lh, p2.head) or playersPartsAreColliding(p2.rh, p2.head):
            if stateMemory["2h"] < DELAY:
                stateMemory["2h"] += 2
            isDetecting = True
        if playersPartsAreColliding(p2.lh, p2.ls) or playersPartsAreColliding(p2.lh, p2.rs) or playersPartsAreColliding(p2.rh, p2.ls) or playersPartsAreColliding(p2.rh, p2.rs):
            if stateMemory["2s"] < DELAY:
                stateMemory["2s"] += 2
            isDetecting = True
        if playersPartsAreColliding(p2.lh, p2.torso) or playersPartsAreColliding(p2.rh, p2.torso):
            if stateMemory["2t"] < DELAY:
                stateMemory["2t"] += 2
            isDetecting = True
        if playersPartsAreColliding(p2.lh, p2.li) or playersPartsAreColliding(p2.lh, p2.ri) or playersPartsAreColliding(p2.rh, p2.li) or playersPartsAreColliding(p2.rh, p2.ri):
            if stateMemory["2t"] < DELAY:
                stateMemory["2t"] += 2
            isDetecting = True

        # ONE touching HIMSELF
        if playersPartsAreColliding(p1.lh, p1.head) or playersPartsAreColliding(p1.rh, p1.head):
            if stateMemory["1h"] < DELAY:
                stateMemory["1h"] += 2
            isDetecting = True
        if playersPartsAreColliding(p1.lh, p1.ls) or playersPartsAreColliding(p1.lh, p1.rs) or playersPartsAreColliding(p1.rh, p1.ls) or playersPartsAreColliding(p1.rh, p1.rs):
            if stateMemory["1s"] < DELAY:
                stateMemory["1s"] += 2
            isDetecting = True
        if playersPartsAreColliding(p1.lh, p1.torso) or playersPartsAreColliding(p1.rh, p1.torso):
            if stateMemory["1t"] < DELAY:
                stateMemory["1t"] += 2
            isDetecting = True
        if playersPartsAreColliding(p1.lh, p1.li) or playersPartsAreColliding(p1.lh, p1.ri) or playersPartsAreColliding(p1.rh, p1.li) or playersPartsAreColliding(p1.rh, p1.ri):
            if stateMemory["1t"] < DELAY:
                stateMemory["1t"] += 2
            isDetecting = True

        for k,v in stateMemory.iteritems():
            if stateMemory[k] >= DELAY: #and msgSentMemory[k] == False:
                cmd = [k + "1"] #Turning On
                osc.sendMsg("/titsPD", cmd, "127.0.0.1", 9999)
                msgSentMemory[k] = True
                print cmd[0]

