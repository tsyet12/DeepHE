from gekko import GEKKO
import numpy as np
import numpy.random as random

m=GEKKO(remote=True)

Nh=random.randint(low=1,high=5) #corresponds to i
Nc=random.randint(low=1,high=5) #corresponds to j


Nhe=2*(Nh+Nc)    #corresponds to m
Cph=np.full(shape=Nh,fill_value=4.2)
Cpc=np.full(shape=Nc,fill_value=4.2)
h=1

Thin=m.Array(m.FV, (Nhe,Nh))
Tcin=m.Array(m.FV,(Nhe,Nc))

#tracking array 
trackhot=[]
trackcold=[]

#random inlet hot temperature case
Th_i0=m.Array(m.Const,(1,Nh))

for Th in Th_i0[0]:
	Th.value=random.uniform(low=30,high=300)   
	trackhot.append(Th.value)
	
#random inlet cold temperature case
Tc_j0=m.Array(m.Const,(1,Nc))
for Tc in Tc_j0[0]:
	Tc.value=random.uniform(low=0,high=min(trackhot)) 
	trackcold.append(Tc.value)

#announce heat exchanger
print("Number of hot stream = ",Nh)
print("Number of cold stream = ", Nc)
print("Hot Stream Temperature=", trackhot)
print("Cold Stream Temperature=", trackcold)


'''
#hot and cold temperature for m>1
Th_i1=m.Array(m.FV,(Nhe-1,Nh))
Tc_j1=m.Array(m.FV,(Nhe-1,Nc))
'''

#outlet temperature
Thin=m.Array(m.Var,(Nhe,Nh))
Tcin=m.Array(m.Var,(Nhe,Nc))

for mf in range(Nhe):
	for i in range(Nh):
		if mf==0:
			Thin[mf][i]=m.Param(value=trackhot[i])
		else:
			Thin[mf][i]=m.FV()
	for j in range(Nc):
		if mf==0:
			Tcin[mf][j]=m.Param(value=trackcold[j])
		else:
			Tcin[mf][j]=m.FV()



'''
Thin=np.concatenate((Th_i0,Th_i1),axis=0)
Tcin=np.concatenate((Tc_j1,Tc_j0),axis=0)
'''


whot=[[m.Var(value=0,lb=0,ub=1,integer=True) for mf in range(Nhe)] for i in range(Nh)]
wcold=[[m.Var(value=0,lb=0,ub=1,integer=True) for mf in range(Nhe)] for j in range(Nc)]	

'''
whot=m.Array(m.Var, (Nhe,Nh)) #initialize binary for stream matching on hot side
wcold=m.Array(m.Var, (Nhe,Nc)) #initialize binary for stream matching on cold side

#integer constraints for binary matrix
for wh1 in whot:
	for wh in wh1:
		wh.value=1
		wh.lower=0
		wh.upper=1
		wh.

for wc1 in wcold:
	for wc in wc1:
		wh.value=1
		wc.lower=0
		wc.upper=1
		wc.integer=True
'''


#define heat integrated
Qm=m.Array(m.FV,Nhe)
#randomly assign some initial values for Qm
for Q in Qm:
	Q.value=random.uniform(low=100,high=10000)

#define dThn dTc
dTh=m.Array(m.FV,(Nh,Nhe))
dTc=m.Array(m.FV,(Nc,Nhe))

#calculate change in temperature
print(Qm)

for i in range(Nh):
	for mf in range(Nhe):
		dTh[i][mf]=whot[i][mf]*Qm[mf]/Cph[i]
for j in range(Nc):
	for mf in range(Nhe):
		dTc[j][mf]=wcold[j][mf]*Qm[mf]/Cpc[j]
		

'''
m.Equations(dTh[i][m]==[[whot.T[i][m]*Qm/Cph[i] for i in range(Nh)] for m in range(Nhe)])

m.Equations(dTc[j][m]==[[wcold.T[j][m]*Qm/Cpc[j] for j in range(Nc)] for m in range(Nhe)])
'''

#Calculate outlet temperature
Thout=m.Array(m.FV,(Nhe,Nh))
Tcout=m.Array(m.FV,(Nhe,Nc))

for mf in range(Nhe):
	for i in range(Nh):
		m.Equations(Thout[mf][i]==Thin[mf][i]-dTh.T[mf][i])
	for j in range(Nc):
		m.Equations(Tcout[mf][j]==Tcin[mf][j]-dTc.T[mf][j])


''''
Thout=[[(Thin[mf][i]-dTh.T[mf][i]) for i in range(Nh)] for mf in range(Nhe)]
Tcout=[[(Tcin[mf][j]+dTc.T[mf][j]) for j in range(Nc)] for mf in range(Nhe)]
'''


#Connect temperature
for mf in range(1,Nhe):
	for i in range(Nh):
		m.Equation(Thin[mf][i] == Thout[mf-1][i])

for mf in range(0,Nhe-1):
	for j in range(Nc):
		m.Equation(Tcin[mf][j] == Tcout[mf+1][j])

#Heat transfer matrix
Thhout=[sum([whot[i][m]*Thout[m][i] for i in range(Nh)]) for m in range(Nhe)]
Tccin=[sum([wcold[j][m]*Tcout[m][j] for j in range(Nc)]) for m in range(Nhe)]





#objective function
m.Obj(-sum(Thhout))

m.options.IMODE = 3
m.options.SOLVER=1
m.solver_options=['minlp_maximum_iterations 1000', 'minlp_gap_tol 0.03']
m.solve(disp=True)



'''

# Initialize Model
m = GEKKO(remote=True)

#help(m)

#define parameter
eq = m.Param(value=40)

#initialize variables
x = [m.Var(value=1,lb=1,ub=5) for i in range(4)]
x[1].value=5
x[2].value=5

#Equations
m.Equation(np.prod([x[i] for i in range(0,4)])>=25)
m.Equation(np.sum([x[i]**2 for i in range(0,4)])==eq)

#Objective
m.Obj(x[0]*x[3]*(x[0]+x[1]+x[2])+x[2])

#Set global options
m.options.IMODE = 3 #steady state optimization

#Solve simulation
m.solve() # solve on public server

#Results
print('')
print('Results')
print('x1: ' + str(x[0].value))
print('x2: ' + str(x[1].value))
print('x3: ' + str(x[2].value))
print('x4: ' + str(x[3].value))
'''