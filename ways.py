def linspace(a,b,step):
  res =[]
  while(a<=b):
    res.append(a)
    a+=step
  return res

def solve():
  fun = linspace

  step = 1
  a=set(fun(0,50,step)) #macri
  b=set(fun(0,50,step)) #massa
  c=set(fun(0,50,step)) #scioli
  d=set(fun(0,20,step)) #binner
  e=set(fun(0,0,step)) #otro
  f=set(fun(0,0,step)) #otro
  suma = 100
  ways=0
#  print a
#  print f
#  print c
#  print d
#  print e

  for _a in a:
    suma = 100-_a
    for _b in b:
      if suma-_b<0:
        break
      suma-=_b
      for _c in c:
        if suma-_c<0:
          break
        suma-=_c
        for _d in d:
          if suma-_d<0:
            break
          suma-=_d
          for _e in e:
            if suma-_e<0:
              break
            suma-=_e
            if suma in f:
              ways+=1
            suma+=_e
          suma+=_d
        suma+=_c
      suma+=_b
    suma+=_a
  return ways



def main():
  print solve()

main()
