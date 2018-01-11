#!/usr/bin/ipython

#
# IMPORT THE OR-TOOLS CONSTRAINT SOLVER
#
from ortools.constraint_solver import pywrapcp

import json # import the "json" module
import sys


def pMain ():


	if len(sys.argv) <2:
		data = json.load(sys.stdin) # read and parse JSON data
	else:
		fname = sys.argv[1]
		with open(fname) as f: # "f" = file object
			data = json.load(f) # read and parse JSON data

	#print (data['options'],type(data))


	#
	# CREATE A SOLVER INSTANCE
	# Signature: Solver(<solver name>)
	slv = pywrapcp.Solver('simple-example')

	# CREATE VARIABLES
	# Signature: IntVar(<min>, <max>, [<name>])
	# Alternative signature: IntVar(<domain as a list>, [<name>])
	'''x1 = slv.IntVar(-2, 5, 'x1')
	x2 = slv.IntVar(-5, 2, 'x2')
	x3 = slv.IntVar(-2, 2, 'x3')
	x3 = slv.IntVar([3], 'x3')'''

	images = data['images']		# HAS to exist
	options = data['options']	# HAS to exist


	defaultWeight = 100000/2

	constM  = len(images)
	setI = range(constM)
	setT = range(constM)
	paramsW = [img['w'] for i,img in enumerate(images)]
	paramsH = [img['h'] for i,img in enumerate(images)]
	paramsAlfa = int(options.get('spaceWeight', defaultWeight));
	paramsBeta = int(options.get('numberWeight', defaultWeight))
	constSU = sum(w * h for w in paramsW for h in paramsH); 

	IW = [ slv.IntVar([w], 'IW%d' % i) for i,w in enumerate(paramsW) ]
	IH = [ slv.IntVar([h], 'IH%d' % i) for i,h  in enumerate(paramsH)] # '''enumerate(paramsH)''' ]
	SU = slv.IntVar([ constSU ], 'SU')
	alfa = slv.IntVar([paramsAlfa], 'alfa')
	beta = slv.IntVar([paramsBeta], 'beta')
	maxInt = slv.IntVar([sys.maxsize], 'maxInt')



	N = slv.IntVar(0, constM, 'N')		# 0<=N<=M

	# al massimo 1 texture per image => 0<=id<=M-1
	IT = [slv.IntVar(0, constM-1, 'IT%d' % i) for i in setI]
	IX = [slv.IntVar(0, sys.maxsize-paramsW[i], 'IX%d' % i) for i in setI]		# da trovare qual'è la massima X e Y => caso peggiore
	IY = [slv.IntVar(0, sys.maxsize-paramsH[i], 'IY%d' % i) for i in setI]		# in ogni caso si toglie la dimensione ???

	TW = [slv.IntVar(0, sys.maxsize, 'TW%d' % i) for i in setT]	# da trovare qual'è la massima X e Y => caso peggiore
	TH = [slv.IntVar(0, sys.maxsize, 'TH%d' % i) for i in setT]	# da trovare qual'è la massima X e Y => caso peggiore

	L = slv.IntVar(0, sys.maxsize, "L")
	ST = slv.IntVar(0, sys.maxsize, "ST")

	f = slv.IntVar(0, sys.maxsize, "f")


#sys.maxsize


	#print ('hey\n',IW,IH, SU, N)


	#
	# BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
	# Signature: Add(<constraint>)
	#slv.Add(2 == x1 + x2)
	slv.Add(f == alfa * L + beta * N)

	slv.Add( L == ST - SU)

	slv.Add( ST == slv.Sum([TW[i]*TH[i] for i in setT]))

	slv.Add( N == slv.Max([IT[i] for i in setI])+1)


	for t in setT:
		slv.Add( TW[t] == slv.Max( [0*maxInt*(1- (IT[i]==t))+ (IX[i]+IW[i])*(IT[i]==t) for i in setI] ) )
		#slv.Add( TH[t] == slv.Min( [maxInt*(1- (IT[i]==t))+ (IY[i]+IW[i])*(IT[i]==t) for i in setI] ) )

	#
	# DEFINE THE SEARCH STRATEGY
	# we will keep this fixed for a few more lectures
	#
	#all_vars = [x1, x2, x3]
	all_vars =  IW + IH + IT + IX + IY + TW + TH + [ f, alfa, L, beta, N, ST, SU, maxInt];
	#DFS (?) Depth First Search
	decision_builder = slv.Phase(all_vars,
	                                slv.INT_VAR_DEFAULT,
	                                slv.INT_VALUE_DEFAULT)


	m1 = None#slv.SearchLog(4000000) #num_branches
	m2 = slv.TimeLimit(3000) #time_limit [milliseconds]
	m3 = slv.Minimize(f, 1)				#  constraint: z <= zbest-step
	# cost function as constraint on variable
	search_monitors = [m1, m2, m3]

	#
	# INIT THE SEARCH PROCESS
	# we will keep this fixed for a few more lectures
	#
	slv.NewSearch(decision_builder ,search_monitors)



	#if slv.solutions() :
	print(all_vars)	
	print()
	#
	# Enumerate all solutions!
	#
	count=0
	while slv.NextSolution():
	    # Here, a solution has just been found. Hence, all variables are bound
	    # and their "Value()" method can be called without errors.
	    # The notation %2d prints an integer using always two "spaces"
	    #print ('x1: %2d, x2: %2d, x3: %2d' % (x1.Value(), x2.Value(), x3.Value()) )
	    if(count%1000==0):
		    print()
		    print('solution %d: ' % count)
		    print(all_vars)
	    count+=1

	print()

	#
	# END THE SEARCH PROCESS
	#
	slv.EndSearch()


	slv.WallTime();
	slv.Branches();
	slv.Failures();

	print ("prova")


if __name__ == "__main__":
	pMain();
