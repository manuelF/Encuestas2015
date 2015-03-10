#!/usr/bin/python2

import redis
import numpy as np
import random

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# S is quantity of points to distribute among all scenarios
S = 100
# F is fraction of points scenarios contribute to outcome pool
F = .6


def loadQuestions():
  f = open("questions.txt", "r")
  lines = [l.strip() for l in f.readlines()]
  f.close()
  return [tuple(map(int, l.split())) for l in lines if l is not ""]


def count(P, arr):
  return len(filter(P, arr))


def matches(scenario, question):
  # Type 1: A>B ?
  if question[1] == 1:
    candA = question[2]
    candB = question[3]
    return scenario[candA - 1] > scenario[candB - 1]
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
    return any(map((lambda x: x > target), scenario))
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

scenarios_q = {}


def getScenariosForQuestion(scenarios, question):
  if question not in scenarios_q:
    all_scenarios = set(scenarios)
    positive_scenarios = set(filter((lambda s: matches(s, question)), scenarios))
    negative_scenarios = (all_scenarios - (positive_scenarios))
    scenarios_q[question] = (positive_scenarios, negative_scenarios)
  return scenarios_q[question]


def initialProbabilites(scenarios):
  N = float(len(scenarios))
  assert (N > 0)
  return {}.fromkeys(scenarios, S / N)


def tick(probabilities_for_scenario, question, response):
  pos_scenarios, neg_scenarios = getScenariosForQuestion(
      probabilities_for_scenario.keys(), question)
  points_lost = 0.0
  winners = 0
  assert(len(pos_scenarios) > 0)
  assert(len(neg_scenarios) > 0)
  if response:
    points_lost = sum([probabilities_for_scenario[s] for s in neg_scenarios])
    winners = len(pos_scenarios)
  else:
    points_lost = sum([probabilities_for_scenario[s] for s in pos_scenarios])
    winners = len(neg_scenarios)
  assert(winners > 0)

  k = float(points_lost) / winners
  for s in pos_scenarios:
    current_probability = probabilities_for_scenario[s]
    if not response:
      k = -current_probability
    new_probability = current_probability + F * k
    probabilities_for_scenario[s] = new_probability

  k = float(points_lost) / winners
  for s in neg_scenarios:
    current_probability = probabilities_for_scenario[s]
    if response:
      k = -current_probability
    new_probability = current_probability + F * k
    probabilities_for_scenario[s] = new_probability


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
  feasibile = []
  for _a in a:
    suma = 100 - _a
    for _b in b:
      if suma - _b < 0:
        break
      suma -= _b
      if suma in c:
        ways += 1
        feasibile.append((_a, _b, suma))
      suma += _b
    suma += _a

  return feasibile


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
  questions = loadQuestions()
  state = initialProbabilites(scenarios)
  random.shuffle(questions)

  for q in questions:
    positive, negative = getResponsesForQuestion(q)
    for i in xrange(positive):
      tick(state, q, True)
    for i in xrange(negative):
      tick(state, q, False)

  li = state.items()

  orden = sorted(li, key=(lambda x: x[1]))
  for i, k in enumerate(orden):
    if i < 10 or i > len(orden) - 10:
      print k

  res = np.divide(np.sum([np.multiply(elem[0], elem[1]) for elem in orden], axis=0), S)
  print res


if __name__ == '__main__':
  main()
