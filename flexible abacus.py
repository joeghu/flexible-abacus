import numpy as np
import os.path
import struct
import statistics
import matplotlib.pyplot as plt

plt.ion()
np.seterr("raise")

dev = False
gens = 5000000
ticks = 1000

def NewIntray():
    if dev == True: print("NewIntray")
    newIntray = np.zeros([256], dtype = np.uint8)

    randomGenerator = np.random.default_rng()

    a = randomGenerator.integers(0, 256)
    b = randomGenerator.integers(0, 256)
    
    for i in range(0, 256, 2):
        newIntray[i] = a
        newIntray[i + 1] = b
            
    return newIntray

def NewOutTray():
    if dev == True: print("NewOutTray")

    newOutTray = np.zeros([4], dtype = np.uint8)

    randomGenerator = np.random.default_rng()
    for i in range(4):
        newOutTray[i] = randomGenerator.integers(0, 256)    
        
    return newOutTray

def Tick(cart, outTray, inTray):
    if dev == True: print("Tick")

    whoIsNext = WhoIsNext(cart)

    extracted = Extract(cart, whoIsNext)
    
    if extracted[9,3] == 0 and dev == True:
        print("could read 0")
        
    if extracted[9,3] == 1 and dev == True:
        print("could read 1")
        

    if extracted[0, 1] < 64: extracted = Processor(cart, extracted)
    elif extracted[0, 1] < 128: cart = Flipper(cart, extracted)
    elif extracted[0, 1] < 192: extracted[6, 2] = inTray[extracted[9, 3]]
    elif extracted[0, 1] < 256: outTray = Writer(outTray, cart, extracted)

    whoWasThat = whoIsNext

    cart = PutExtractedBackInCart(cart, extracted, whoWasThat)
    
    return cart, outTray

def PutExtractedBackInCart(cart, extracted, whoWasThat):
    
    cart = cart.astype(np.int32)
    extracted = extracted.astype(np.int32)
        
    ink = extracted[0, 2]
    bounce = extracted[0, 3]

    if (ink + bounce) == 0:
        ink = 1
        bounce = 1

    for s in range(4):
        for rv in range(3):
            cart[s, whoWasThat[s], 6, rv] = ((bounce*cart[s, whoWasThat[s], 6, rv]) +
                                             (ink*extracted[6, rv]))/(ink + bounce)
            
    cart = cart.astype(np.uint8)
    
    return cart

def WhoIsNext(cart):
    if dev == True: print("WhoIsNext")
    randomGenerator = np.random.default_rng()
    whoIsNext = [0, 0, 0, 0]
    for s in range(4):
        totalShelfProbPoints = np.uint32(0)
        if dev == True: print(type(totalShelfProbPoints))
        if dev == True: print(totalShelfProbPoints)
        for b in range(256):            
            totalShelfProbPoints = totalShelfProbPoints + cart[s, b, 0, 0]
        if dev == True: print("S", s, "Total prob points", totalShelfProbPoints)

        if totalShelfProbPoints == 0: rollTo = 0
        else: rollTo = randomGenerator.integers(totalShelfProbPoints)

        
        if dev == True: print("rollTo", rollTo)
        distanceRolled = np.uint32(1)
        bookIndexOnWhichExceededRollTo = 0
        for b in range(256):
            distanceRolled = distanceRolled + cart[s, b, 0, 0]
            if distanceRolled > rollTo:
                bookIndexOnWhichExceededRollTo = b
                break
        if dev == True: print("bookIndexOnWhichExceededRollTo", bookIndexOnWhichExceededRollTo)
        whoIsNext[s]= bookIndexOnWhichExceededRollTo
    if dev == True: print("whoIsNext", whoIsNext) 
    return whoIsNext

def Extract(cart, whoIsNext):
    if dev == True: print("Extract")
    cart = cart.astype(np.uint64)
    extracted = np.zeros([11, 4], dtype = np.uint64)
    for c in range(11):
        for r in range(4):
            extracted[c, r] = ( cart[0, whoIsNext[0], c, r] +
                                cart[1, whoIsNext[1], c, r] +
                                cart[2, whoIsNext[2], c, r] +
                                cart[3, whoIsNext[3], c, r] )/4
    extracted = extracted.astype(np.uint8)
    if dev == True: print(extracted)
    return extracted

def Processor(cart, extracted):
    if dev == True: print("Processor")
    
    iPV0 = GetOPV(cart, [extracted[1, 0], extracted[2, 0],
                         extracted[3, 0], extracted[4, 0]])
    iPV1 = GetOPV(cart, [extracted[1, 1], extracted[2, 1],
                         extracted[3, 1], extracted[4, 1]])

    aMP0 = extracted[6, 0]
    aMP1 = extracted[6, 1]

    try:
        ampedIPV0 = iPV0
        if extracted[5, 0] < 64: ampedIPV0 = iPV0 / aMP0
        elif extracted[5, 0] < 128: ampedIPV0 = iPV0 - aMP0
        elif extracted[5, 0] < 192: ampedIPV0 = iPV0 + aMP0
        elif extracted[5, 0] < 256: ampedIPV0 = iPV0 * aMP0

        ampedIPV1 = iPV1
        if extracted[5, 1] < 64: ampedIPV1 = iPV1 / aMP1
        elif extracted[5, 1] < 128: ampedIPV1 = iPV1 - aMP1
        elif extracted[5, 1] < 192: ampedIPV1 = iPV1 + aMP1
        elif extracted[5, 1] < 256: ampedIPV1 = iPV1 * aMP1

        oPV = 0
        if extracted[7, 0] < 64: oPV = ampedIPV0 / ampedIPV1
        elif extracted[7, 0] < 128: oPV = ampedIPV0 - ampedIPV1
        elif extracted[7, 0] < 192: oPV = ampedIPV0 + ampedIPV1
        elif extracted[7, 0] < 256: oPV = ampedIPV0 * ampedIPV1
        extracted[6, 2] = oPV

        outa0 = extracted[9, 0]
        outa1 = extracted[9, 1]

        ampedOPV0 = oPV
        if extracted[8, 0] < 64: ampedOPV0 = oPV / outa0
        elif extracted[8, 0] < 128: ampedOPV0 = oPV - outa0
        elif extracted[8, 0] < 192: ampedOPV0 = oPV + outa0
        elif extracted[8, 0] < 256: ampedOPV0 = oPV * outa0

        ampedOPV1 = oPV
        if extracted[8, 1] < 64: ampedOPV1 = oPV / outa1
        elif extracted[8, 1] < 128: ampedOPV1 = oPV - outa1
        elif extracted[8, 1] < 192: ampedOPV1 = oPV + outa1
        elif extracted[8, 1] < 256: ampedOPV1= oPV * outa1

        if extracted[10, 0] < 64: extracted[6, 0] = extracted[6, 0] / ampedOPV0
        elif extracted[10, 0] < 128: extracted[6, 0] = extracted[6, 0] - ampedOPV0
        elif extracted[10, 0] < 192: extracted[6, 0] = extracted[6, 0] + ampedOPV0
        elif extracted[10, 0] < 256: extracted[6, 0] = extracted[6, 0] * ampedOPV0

        if extracted[10, 1] < 64: extracted[6, 1] = extracted[6, 1] / ampedOPV1
        elif extracted[10, 1] < 128: extracted[6, 1] = extracted[6, 1] - ampedOPV1
        elif extracted[10, 1] < 192: extracted[6, 1] = extracted[6, 1] + ampedOPV1
        elif extracted[10, 1] < 256: extracted[6, 1] = extracted[6, 1] * ampedOPV1

    except Exception as exception:
        if dev == True: print(type(exception))

    return extracted

def Flipper(cart, extracted):
    if dev == True: print("Flipper")
    
    flipperValue = GetOPV(cart, [extracted[1, 2], extracted[2, 2],
                                 extracted[3, 2], extracted[4, 2]])

    if extracted[7, 2] < 64: lf0 = 0
    elif extracted[7, 2] < 128: lf0 = 1
    elif extracted[7, 2] < 192: lf0 = 2
    elif extracted[7, 2] < 256: lf0 = 3

    lf1 = extracted[8, 2]

    if extracted[9, 2] < (23*1): lf2 = 0
    elif extracted[9, 2] < (23*2): lf2 = 1
    elif extracted[9, 2] < (23*3): lf2 = 2
    elif extracted[9, 2] < (23*4): lf2 = 3
    elif extracted[9, 2] < (23*5): lf2 = 4
    elif extracted[9, 2] < (23*6): lf2 = 5
    elif extracted[9, 2] < (23*7): lf2 = 6
    elif extracted[9, 2] < (23*8): lf2 = 7
    elif extracted[9, 2] < (23*9): lf2 = 8
    elif extracted[9, 2] < (23*10): lf2 = 9
    elif extracted[9, 2] < 256: lf2 = 10

    if extracted[10, 2] < 64: lf3 = 0
    elif extracted[10, 2] < 128: lf3 = 1
    elif extracted[10, 2] < 192: lf3 = 2
    elif extracted[10, 2] < 256: lf3 = 3

    cart[lf0, lf1, lf2, lf3] = flipperValue    
    
    return cart

def Writer(outTray, cart, extracted):
    if dev == True: print("Writer")

    valueToWrite = GetOPV(cart, [extracted[1, 3], extracted[2, 3],
                                 extracted[3, 3], extracted[4, 3]])

    if extracted[10, 3] < 64: lwrite = 0
    elif extracted[10, 3] < 128: lwrite = 1
    elif extracted[10, 3] < 192: lwrite = 2
    elif extracted[10, 3] < 256: lwrite = 3

    outTray[lwrite] = valueToWrite
        
    return outTray

def InterpretCartCoordinateUNUSED(fourUint8s):
        
    cartAddress = [0, 0, 0, 0]

    if fourUint8s[0] < 64: cartAddress[0] = 0
    elif fourUint8s[0] < 128: cartAddress[0] = 1
    elif fourUint8s[0] < 192: cartAddress[0] = 2
    elif fourUint8s[0] < 256: cartAddress[0] = 3

    cartAddress[1] = fourUint8s[1]

    if fourUint8s[2] < 23: cartAddress[2] = 0
    elif fourUint8s[2] < (23*2): cartAddress[2] = 1
    elif fourUint8s[2] < (23*3): cartAddress[2] = 2
    elif fourUint8s[2] < (23*4): cartAddress[2] = 3
    elif fourUint8s[2] < (23*5): cartAddress[2] = 4
    elif fourUint8s[2] < (23*6): cartAddress[2] = 5
    elif fourUint8s[2] < (23*7): cartAddress[2] = 6
    elif fourUint8s[2] < (23*8): cartAddress[2] = 7
    elif fourUint8s[2] < (23*9): cartAddress[2] = 8
    elif fourUint8s[2] < (23*10): cartAddress[2] = 9
    elif fourUint8s[2] < 256: cartAddress[2] = 10

    if fourUint8s[3] < 64: cartAddress[3] = 0
    elif fourUint8s[3] < 128: cartAddress[3] = 1
    elif fourUint8s[3] < 192: cartAddress[3] = 2
    elif fourUint8s[3] < 256: cartAddress[3] = 3
    
    return cartAddress
    
def GetOPV(cart, address):
    extractedToGetOPV = Extract(cart, address)
    oPV = extractedToGetOPV[6, 2]
    return oPV

def Score(inTray, outTray):
    if dev == True: print("Score")

    first2inTray = np.zeros([2], dtype = np.uint8)
    for i in range(2):
        first2inTray[i] = inTray[i]

    first2inTrayBytes = first2inTray.tobytes()
    first2inTrayUInt16Tuple = struct.unpack("H", first2inTrayBytes)

    inTrayNumber = first2inTrayUInt16Tuple[0]

    outTrayNumber = outTray[0]
    
    correctAnswer = int(inTrayNumber**0.5)
    print("inTrayNumber", inTrayNumber)
    print("correctAnswer", correctAnswer)
    print("outTrayNumber", outTrayNumber)
    
    difference = abs(float(correctAnswer) - float(outTrayNumber))
    print("difference", difference)

    score = 1

    if difference > 0:
        score = 1 - (difference / 256)
    
  
    alteredScore = ( (score*10)**3 ) /1000

    scores = [score, alteredScore]
    
    return scores


def NewCart():
    randomGenerator = np.random.default_rng()

    newCart = np.zeros([4, 256, 11, 4], dtype = np.uint8)

    for s in range(4):
        for b in range(256):
            for c in range(11):
                for r in range(4):
                    newCart[s, b, c, r] = randomGenerator.integers(0,256)

    return newCart

def NewChallenger(fromCart):
    randomGenerator = np.random.default_rng()

    for s in range(4):
        for b in range(256):
            for c in range(11):
                for r in range(4):
                    incOrDec = randomGenerator.integers(0, 2)
                    amount = randomGenerator.integers(0, 10)
                    if incOrDec == 0 and fromCart[s, b, c, r] + amount < 256 : 
                        fromCart[s, b, c, r] = fromCart[s, b, c, r] + amount
                    if incOrDec == 1 and fromCart[s, b, c, r] - amount >= 0:
                        fromCart[s, b, c, r] = fromCart[s, b, c, r] - amount
                    
    return fromCart

print("*****FLEXIBLE ABACUS*****")

if os.path.isfile("experimentcart.npy"):
    existing = np.load("experimentcart.npy")
    print("Loaded experimentcart.npy")    
else:
    print("experimentcart.npy not found.")
    existing = NewCart()
    print("Created new cart.")
    np.save("experimentcart", existing)
    print("Saved new cart to experimentcart.npy")

if os.path.isfile("cartstats.npy"):
    cartstats = np.load("cartstats.npy")
    allExistingScoresSoFar = list(cartstats)
    print("Loaded cartstats.npy")    
else:
    print("cartstats.npy not found.")
    print("Will create new cartstats")
    allExistingScoresSoFar = []

print("")

print("This AI accepts an array of 256 uint8 values as input.")
print("Edit the NewIntray definition to supply input in this form.")
print("It outputs an array of 4 uint8 values to the outTrayExisting.")
print("Edit the Score definition to set how outputs are scored.")
print("Edit the number of ticks to set processing time per generation.")
print("Left unedited, it will attempt to estimate approximate square roots.")

print("")

print("Press any key to continue.")
input()

existingScoresToday = []

for g in range(gens):
    print("G", len(allExistingScoresSoFar))
    print(ticks, "ticks")
    
    initialExisting = np.copy(existing)

    inTray = NewIntray()
    outTrayExisting = NewOutTray()
    for t in range(ticks):
        if dev == True: print("existing T", t)
        existing, outTrayExisting = Tick(existing, outTrayExisting, inTray)

    scoreExisting = Score(inTray, outTrayExisting)
    print("scoreExisting", scoreExisting[0])

    existingScoresToday.append(scoreExisting[0])
    allExistingScoresSoFar.append(scoreExisting[0])
    np.save("cartstats", np.array(allExistingScoresSoFar))
    
    plt.clf()

    plt.xlabel("Score (0 = worst, 1 = best)")
    plt.ylabel("Total occurences since generation 0")

    plt.hist(allExistingScoresSoFar, bins = 20)

    plt.pause(0.1)
    
    if scoreExisting == 0: continue
     

    challenger = NewChallenger(initialExisting)
    
    initialChallenger = np.copy(challenger)

    
    outTrayChallenger = NewOutTray()
    for t in range(ticks):
        if dev == True: print("challenger T", t)
        challenger, outTrayChallenger = Tick(challenger, outTrayChallenger, inTray)

    scoreChallenger = Score(inTray, outTrayChallenger)
    print("scoreChallenger", scoreChallenger[0])

    
    if scoreChallenger[0] > scoreExisting[0]:
        existing = np.copy(initialChallenger)
        np.save("experimentcart", existing)
        print("Saved a new cart to experimentcart.npy")
    else: existing = np.copy(initialExisting)

    print("")

input()     


        

    

