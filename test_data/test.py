#!/bin/python
# Usage:
#    python test.py [# of responses] [evaluated scenario]

from datetime import datetime
import requests
import random
import json
import sys

repeats = eval(sys.argv[1])
basic_scenario = eval(sys.argv[2])


def getQuestion():
    q = json.loads(requests.get('http://162.220.15.210:8000/getdebug/').text)
    print q
    return q

def answerQuestion(user_id, question_id, answer):
    ans = 'Y' if answer else 'N'
    response = "http://162.220.15.210:8000/respond/{0}/{1}/{2}".format(user_id, question_id, ans)
    print response
    r = requests.get(response)

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
    start_time = datetime.now()
    for i in xrange(repeats):
        user_id = random.randint(1, 1000000)
        new_question = getQuestion()
        args = (new_question["Q_id"], new_question["Q_Type"], new_question["Arg1"], new_question["Arg2"])
        ans = matches (basic_scenario, args)
        answerQuestion(user_id, new_question["Q_id"], ans)
        print i, str(datetime.now()-start_time)
        start_time = datetime.now()

if __name__ == '__main__':
    main()
