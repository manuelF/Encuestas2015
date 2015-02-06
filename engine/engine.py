#!/usr/bin/python2

import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)


def loadQuestions():
    f = open("questions.txt", "r")
    lines = [l.strip() for l in f.readlines()]
    f.close()
    return [map(int, l.split()) for l in lines if l is not ""]


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

memo = {}


def get(q_id, response):
    key = (q_id, response)
    if key not in memo:
        res = r.scard("q:" + str(q_id) + "r:Y")
        memo[(q_id, True)] = res
        res = r.scard("q:" + str(q_id) + "r:N")
        memo[(q_id, False)] = res
    return memo[key]


def getResponsesForQuestion(question):
    def question_id(x):
        return x[0]

    positive = get(question_id(question), True)
    negative = get(question_id(question), False)

    return (positive, negative)


def solve(scenarios, question):
    positive, negative = getResponsesForQuestion(question)

    for s in scenarios.keys():
        if matches(s, question):
            scenarios[s] += positive
        else:
            scenarios[s] += negative


def generateScenarios():
    def linspace(a, b, step):
        res = []
        while(a <= b):
            res.append(a)
            a += step
        return res

    fun = linspace

    step = 1
    a = set(fun(0, 60, step))  # macri
    b = set(fun(0, 60, step))  # massa
    c = set(fun(0, 60, step))  # scioli
    suma = 100
    ways = 0
    feasbile = []
    for _a in a:
        suma = 100 - _a
        for _b in b:
            if suma - _b < 0:
                break
            suma -= _b
            if suma in c:
                ways += 1
                feasbile.append((_a, _b, suma))
            suma += _b
        suma += _a

    return feasbile


def votesPerCandidate(scenarios):
    # Count how many votes does a scenario receive, if the candidate is the
    # winner
    candidates_votes = {}
    for s in scenarios:
        for index, candidate in enumerate(s):
            if candidate == max(s):
                current = candidates_votes.setdefault(index + 1, 0)
                candidates_votes[index + 1] = current + scenarios[s]
    total_votes = float(
        sum([candidates_votes[k] for k in candidates_votes])) / 100.
    for c in candidates_votes:
        print "Candidate " + str(c) + ": " + str(candidates_votes[c] / total_votes) + " votes"


def main():
    scenarios = generateScenarios()
    hit_scenarios = {}.fromkeys(scenarios, 0)
    questions = loadQuestions()
    for q in questions:
        solve(hit_scenarios, q)
    votesPerCandidate(hit_scenarios)
    for h in hit_scenarios:
        print str(hit_scenarios[h]) + " - " + str(h)


if __name__ == '__main__':
    main()
