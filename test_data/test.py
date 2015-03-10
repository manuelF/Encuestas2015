#!/bin/python
import requests
import json

basic_scenario = (45, 35, 20)



def getQuestion():
    q = requests.get('http://162.220.15.210:8000/getdebug/')
    return json.loads(q.text)





def matches(scenario, question):
    # Type 1: A<B ?
    if question[1] == 1:
        candA = question[2]
        candB = question[3]
        return scenario[candA - 1] < scenario[candB - 1]
    # Type 2: A >= X%?
    if question[1] == 2:
        candA = question[2]
        target = question[3]
        return scenario[candA - 1] >= target
    # Type 3: A < X% ?
    if question[1] == 3:
        candA = question[2]
        target = question[3]
        return scenario[candA - 1] < target
    # Type 4: Is there a cand >= X% ?
    if question[1] == 4:
        target = question[2]
        return any(map((lambda x: x >= target), scenario))
    # Type 5: Is the distance between 1st and 2nd at least X% ?
    if question[1] == 5:
        target = question[2]
        sort = sorted(scenario)
        return sort[-1] - target >= sort[-2]
    # Type 6: Is there at least N candidates with at least X%?
    if question[1] == 6:
        N = question[2]
        target = question[3]
        return N >= len([N for x in scenario if x >= target])

    print "Error: " + str(scenario) + str(question)
    assert(False)

def main():
    asd = getQuestion()

if __name__ == '__main__':
    main()
