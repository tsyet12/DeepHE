
from gekko import GEKKO
import numpy as np
import numpy.random as random
import csv

def HE_solve(T_hot,T_cold,Num_HE):

  inf=1000000000

  m=GEKKO(remote=True)
  '''
  Nh=random.randint(low=1,high=4) #corresponds to i
  Nc=random.randint(low=1,high=4) #corresponds to j
  Nhe=5    #corresponds to m
  '''

  Nh=T_hot.__len__() #corresponds to i
  Nc=T_cold.__len__() #corresponds to j
  Nhe=Num_HE    #corresponds to m

  #Initialize Cp array
  Cph=[m.Const(value=37.52) for i in range(Nh)]
  Cpc=[m.Const(value=4.23) for i in range(Nc)]

  #Initialize h array
  hh=[m.Const(value=1) for i in range(Nh)]
  hc=[m.Const(value=1) for i in range(Nc)]

  EMAT=[m.Const(value=10) for i in range(Nhe)]

  objMES=True

  #Temperature for Hot Stream

  #tracking array 
  trackhot=[]
  trackcold=[]

  '''
  #random inlet hot temperature case
  Th_i0=m.Array(m.Const,(1,Nh))
  Thf=[m.Const(value=200) for i in range(Nh)]#250
  for Th in Th_i0[0]:
    #Th.value=random.uniform(low=260,high=400) #random inlet   
    Th.value=400
    trackhot.append(Th.value)

  #random inlet cold temperature case
  Tc_j0=m.Array(m.Const,(1,Nc))
  Tcf=[m.Const(value=150) for i in range(Nc)]

  for Tc in Tc_j0[0]:
    #Tc.value=random.uniform(low=0,high=50) 
    Tc.value=40
    trackcold.append(Tc.value)
  '''
  #random inlet hot temperature case
  Th_i0=m.Array(m.Const,(1,Nh))
  Thf=[m.Const(value=250) for i in range(Nh)]#250

  for i in range(Nh):
    #Th.value=random.uniform(low=260,high=400) #random inlet   
    Th_i0[0][i].value=T_hot[i]
    trackhot.append(Th_i0[0][i].value)

  #random inlet cold temperature case
  Tc_j0=m.Array(m.Const,(1,Nc))
  Tcf=[m.Const(value=60) for i in range(Nc)]

  for i in range(Nc):
    #Tc.value=random.uniform(low=0,high=50) 
    Tc_j0[0][i].value=T_cold[i]
    trackcold.append(Tc_j0[0][i].value)

  #announce heat exchanger
  print("Number of hot stream = ",Nh)
  print("Number of cold stream = ", Nc)
  print("Hot Stream Temperature=", trackhot)
  print("Cold Stream Temperature=", trackcold)

  #Integrated Heat
  Qm=[m.Var(lb=0,ub=inf) for i in range(Nhe)]

  #Heat cascade
  Thin=[[ m.Var(lb=0,ub=inf) for i in range(Nhe)] for i in range(Nh)]
  Thout=[[ m.Var(lb=0,ub=inf) for i in range(Nhe)] for i in range(Nh)]

  #Cold cascade
  Tcin=[[ m.Var(lb=0,ub=inf) for i in range(Nhe)] for i in range(Nc)]
  Tcout=[[ m.Var(lb=0,ub=inf) for i in range(Nhe)] for i in range(Nc)]

  #Heat and cool binary
  wh=[[m.Var(lb=-0.1,ub=1.1,integer=True) for i in range(Nhe)]for i in range(Nh)]
  wc=[[m.Var(lb=-0.1,ub=1.1,integer=True) for i in range(Nhe)]for i in range(Nc)]

  for k in range(Nhe):
    m.Equation(sum([wh[j][k]for j in range(Nh)])==1)
    m.Equation(sum([wc[j][k]for j in range(Nc)])==1)

  #Eq2 First row of Heat Matrix
  for i in range(Nh):
    m.Equation(Thin[i][0]==Th_i0[0][i])

  #Eq5 First Row of Cool Matrix
  for i in range(Nc):
    m.Equation(Tcin[i][Nhe-1]==Tc_j0[0][i])

  #Eq3 and Eq6 Heat balance and Eq4 and Eq7 cascade operation
  for k in range(Nhe):
    for i in range(Nh):
      m.Equation(Thout[i][k]==Thin[i][k]-wh[i][k]*Qm[k]/Cph[i])
      if k!=0:
        m.Equation(Thin[i][k]==Thout[i][k-1])
    for j in range(Nc):
      m.Equation(Tcout[j][k]==Tcin[j][k]+wc[j][k]*Qm[k]/Cpc[j])
      if k!=0:
        m.Equation(Tcin[j][k-1]==Tcout[j][k])

  #Additional cooler and heater
  Qcu=[m.Var(lb=0,ub=inf)for i in range(Nh)]
  Qhu=[m.Var(lb=0,ub=inf)for i in range(Nc)]


  #for MES Objective
  whQ=[[m.Var(value=0,lb=0,ub=inf) for i in range(Nhe)]for i in range(Nh)]
  wcQ=[[m.Var(value=0,lb=0,ub=inf) for i in range(Nhe)]for i in range(Nc)]

  for k in range(Nhe):
    for i in range(Nh):
      m.Equation(whQ[i][k]==wh[i][k]*Qm[k])

  for j in range(Nc):
    m.Equation(wcQ[j][k]==wc[j][k]*Qm[k])

  for i in range(Nh):
    m.Equation(Qcu[i]==Cph[i]*(Th_i0[0][i]-Thf[i])-sum(whQ[i]))



  for i in range(Nc):
    m.Equation(Qhu[i]==Cpc[i]*(Tcf[i]-Tc_j0[0][i])-sum(wcQ[i]))

  if objMES==True:
    m.Obj(sum(Qcu)+sum(Qhu))


  #Temperature of Recovert Heat Exchanger
  Thhin=[m.Var(lb=0,ub=inf)for i in range(Nhe)]
  Thhout=[m.Var(lb=0,ub=inf)for i in range(Nhe)]
  Tccin=[m.Var(lb=0,ub=inf)for i in range(Nhe)]
  Tccout=[m.Var(lb=0,ub=inf)for i in range(Nhe)]

  for k in range(Nhe):
    m.Equation(Thhout[k]==sum([wh[i][k]*Thout[i][k] for i in range(Nh)]))
    m.Equation(Tccout[k]==sum([wc[i][k]*Tcout[i][k] for i in range(Nc)]))
    m.Equation(Thhin[k]==sum([wh[i][k]*Thin[i][k] for i in range(Nh)]))
    m.Equation(Tccin[k]==sum([wc[i][k]*Tcin[i][k] for i in range(Nc)]))

  #Feasibility constraint

  for k in range(Nhe):
    m.Equation(Thhin[k] >= Tccout[k]+EMAT[k])
    m.Equation(Thhout[k] >= Tccin[k] + EMAT[k])

  for i in range(Nh):
    m.Equation(sum(whQ[i])>=0)
    m.Equation(sum(whQ[i])<=Cph[i]*(Th_i0[0][i]-Thf[i]))
    m.Equation(Qcu[i]>=0)
    m.Equation(Qcu[i]<= Cph[i]*(Th_i0[0][i]-Thf[i]))
    m.Equation(Thout[i][Nhe-1]>=Thf[i])#Temperature down in cooler

  for j in range(Nc):
    m.Equation(sum(wcQ[j])>=0)
    m.Equation(sum(wcQ[j])<=Cpc[j]*(Tcf[j]-Tc_j0[0][j]))
    m.Equation(Qhu[j]>=0)
    m.Equation(Tcout[j][0]<=Tcf[j]) #Temperature up in heater
    m.Equation(Qhu[j]<= Cpc[j]*(Tcf[j]-Tc_j0[0][j])) 

  '''
  #Making sure that temperature follows sequence
  for k in range(Nhe-1):
    for i in range(Nh):
      m.Equation(Thout[i][k]>=Thout[i][k+1]) #follow sequence
    for j in range(Nc):
      m.Equation(Tcout[j][k]<=Tcout[i][k+1]) #follow sequence
  '''
  #Eqn 19-22 Cooler Heater Temperature
  Tcooler_hin=[m.Var(lb=0,ub=inf) for i in range(Nh)]
  Tcooler_hout=[m.Var(lb=0,ub=inf) for i in range(Nh)]
  Theater_cin=[m.Var(lb=0,ub=inf) for i in range(Nc)]
  Theater_cout=[m.Var(lb=0,ub=inf) for i in range(Nc)]

  for i in range(Nh):
    m.Equation(Tcooler_hin[i]==Thout[i][Nhe-1])
    m.Equation(Tcooler_hout[i]==Thf[i])
    #m.Equation(Thf[i]>=Thout[i][Nhe-1]) #thf constrain
  for i in range(Nc):
    m.Equation(Theater_cin[i]==Tcout[i][0])
    m.Equation(Theater_cout[i]==Tcf[i])
    #m.Equation(Tcf[i]<=Tcout[i][0]) #tcf constrain


  m.options.SOLVER=1
  m.solver_options = ['minlp_maximum_iterations 5000', \
  # minlp iterations with integer solution
  'minlp_max_iter_with_int_sol 5000', \
  # treat minlp as nlp
  'minlp_as_nlp 0', \
  # nlp sub-problem max iterations
  'nlp_maximum_iterations 2000', \
  # 1 = depth first, 2 = breadth first
  'minlp_branch_method 1', \
  # maximum deviation from whole number
  'minlp_integer_tol 0.001', \
  # covergence tolerance
  'minlp_gap_tol 0.00001']
  try:
    m.solve()
  except:
    return inf
  print(sum([Cph[i].value*(Th_i0[0][i].value-Thf[i].value) for i in range(Nh)]))
  print(sum([Cpc[i].value*(Tcf[i].value-Tc_j0[0][i].value) for i in range(Nc)]))
  print("Number of hot stream = ",Nh)
  print("Number of cold stream = ", Nc)
  print("Hot Stream Temperature=", trackhot)
  print("Cold Stream Temperature=", trackcold)
  print("Heat Recovered:",Qm)
  print("Hot binary:")
  print(wh)
  print("Cold binary:")
  print(wc)
  print("Hot Temperature in:",Thhin)
  print("Hot Temperature out:", Thout)
  print("Cooler Temperature:",Tcooler_hin,Tcooler_hout)
  print("Cold Temperature in:", Tcin)
  print("Cold Temperature out:",Tcout)
  print("Heater Temperature:",Theater_cin,Theater_cout)
  
  seqH=[None]*Nhe
  seqC=[None]*Nhe
  
  for j in range(Nhe):
    for i in range(Nh):
      if wh[i][j].value==[1.0] or wh[i][j].value==1.0:
        seqH[j]=i+1
  print(seqH)
  
  for j in range(Nhe):
    for i in range(Nc):
      if wc[i][j].value==[1.0] or wc[i][j].value==1.0:
        seqC[j]=i+1
  print(seqC)
  
  with open('data/train.csv', 'a', newline='') as fd:
    writer=csv.writer(fd)
    writer.writerow([str(T_hot+T_cold),str(seqH),str(seqC),str(Qm),str(m.options.objfcnval)])
  return m.options.objfcnval


objective_list=[]
for i in range(46):
  
  #Nh=random.randint(low=1,high=4)
  #Nc=random.randint(low=1,high=4)
  Nh=3
  Nc=3
  Hot_list=[]
  Cold_list=[]
  
  for j in range(Nh):
    Hot_list.append(random.uniform(low=250,high=400))
    
  for k in range(Nc):
    Cold_list.append(random.uniform(low=25,high=60))
    
  answer=HE_solve(Hot_list,Cold_list,5)
  objective_list.append(answer)
print(objective_list)
  



#answer=HE_solve([350,310,290],[50,38,30],4)
