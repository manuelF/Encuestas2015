#!/bin/python
import requests
import json

def getQuestion():
  q = requests.get('http://162.220.15.210:8000/getdebug/')
  print q.text
  return json.loads(q.text)


asd = getQuestion()

