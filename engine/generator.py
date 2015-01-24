#!/usr/bin/python2


def linspace(a, b, step):
    res = []
    while(a <= b):
        res.append(a)
        a += step
    return res

seqNumber = 1


def printEm(x):
    global seqNumber
    print str(seqNumber) + " " + " ".join(map(str, x))
    seqNumber += 1


def main():

    candidates = 3
    aMoreThanB = [(1, a, b) for a in xrange(1, candidates + 1)
                  for b in xrange(1, candidates + 1) if a != b]

    minVotes = 5
    maxVotes = 60
    step = 5
    aMoreThanX = [(2, a, x) for a in xrange(1, candidates + 1)
                  for x in linspace(minVotes, maxVotes, step)]
    aLessThanX = [(3, a, x) for a in xrange(1, candidates + 1)
                  for x in linspace(minVotes, maxVotes, step)]

    anyCandOverX = [(4, x) for x in linspace(minVotes, maxVotes, step)]

    minDistance = 2
    maxDistance = 30
    stepDistance = 3
    distanceBetweenFirstAndSecond = [
        (5, x) for x in linspace(minDistance, maxDistance, stepDistance)]

    generated = aMoreThanB
    generated += aMoreThanX + aLessThanX
    generated += anyCandOverX
    generated += distanceBetweenFirstAndSecond
    map(printEm, generated)
    return

if __name__ == '__main__':
    main()
