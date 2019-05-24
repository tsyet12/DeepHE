from gekko import GEKKO
m1=GEKKO(remote=False)
inf=1000000000000

Th0=m1.Const(value=400,name="Th0")
Tc0=m1.Const(value=40,name="Tc0")
Thf=m1.Const(value=200,name="Thf")
Tcf=m1.Const(value=150,name="Tcf")

Q1=m1.Var(value=20,lb=0,ub=inf,name="Q1")
Qh=m1.Var(value=20,lb=0,ub=inf,name="Qh")
Qc=m1.Var(value=20,lb=0,ub=inf,name="Qc")

Th=m1.Var(lb=0,ub=inf,name="Th")
Tc=m1.Var(lb=0,ub=inf,name="Tc")

w1=m1.Var(value=0,lb=0,ub=1,integer=True)
w2=m1.Var(value=0,lb=0,ub=1,integer=True)


m1.Equation(Th==Th0-(w1)*Q1/4.2)
m1.Equation(Thf==Th-Qh/4.2)
#m1.Equation(Th>=Thf)


m1.Equation(Tc==Tc0+(w2)*Q1/4.2)
m1.Equation(Tcf==Tc+Qc/4.2)
#m1.Equation(Tc>=Tcf)



m1.options.SOLVER=1
m1.solver_options = ['minlp_maximum_iterations 500', \
# minlp iterations with integer solution
'minlp_max_iter_with_int_sol 10', \
# treat minlp as nlp
'minlp_as_nlp 0', \
# nlp sub-problem max iterations
'nlp_maximum_iterations 50', \
# 1 = depth first, 2 = breadth first
'minlp_branch_method 1', \
# maximum deviation from whole number
'minlp_integer_tol 0.05', \
# covergence tolerance
'minlp_gap_tol 0.01']

m1.Obj(Qh+Qc)
m1.solve()

#answer obj = 378.0000
print(Q1.value)
print(Qh.value,Qc.value)
print(w1.value,w2.value)