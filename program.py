#!/usr/bin/python3.6

#
# IMPORT THE OR-TOOLS CONSTRAINT SOLVER
#
from ortools.constraint_solver import pywrapcp

import json # import the "json" module
import sys
import math

def clamp(val: int, minimum: int, maximum: int ):
	#if minimum>maximum: print('errore in clamp, min>max!!')
	return max(min(val, maximum), minimum)



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


	'''def getNVar( isFixedNum: bool, constMaxN: int, constM: int):
		if(isFixedNum):	N = slv.IntVar([constMaxN], 'N')
		else:			N = slv.IntVar(1, constM, 'N')		# 1<=N<=M
		return N;'''

	def getNVar( N: int, constMaxN: int):
		if(N>0):	N = slv.IntVar([N], 'N')
		else:			N = slv.IntVar(1, constMaxN, 'N')		# 1<=N<=M
		return N;

	# 0 vuol dire che l'immagine NON ha area!
	def getTextureDims(maxDimension: int, name: str, powOf2: bool, setT):
		if(powOf2):
			pows = [2**i for i in range(math.ceil(math.log2(maxDimension)))]	# da 2**0 a 2**N
			dims = [slv.IntVar(pows, '%s%d' % (name,t)) for t in setT]
		else:	dims = [slv.IntVar(0, maxDimension, '%s%d' % (name,t)) for t in setT]
		return dims;

	# CREATE VARIABLES
	# Signature: IntVar(<min>, <max>, [<name>])
	# Alternative signature: IntVar(<domain as a list>, [<name>])

	images = data['images']		# HAS to exist
	options = data['options']	# HAS to exist
	textureOptions = options['textures'];
	print('options:', options);


	defaultWeight = 100000/2


	constM  = len(images)
	constMaxN = clamp(int(textureOptions.get('maxNumber', constM)), 1, constM)

	setI = range(constM)
	setT = range(constMaxN)
	paramsW = [ img['w'] for i,img in enumerate(images) ]
	paramsH = [ img['h'] for i,img in enumerate(images) ]
	paramAlfa = int(options.get('spaceWeight', defaultWeight));
	paramBeta = int(options.get('numberWeight', defaultWeight));
	if(paramAlfa*paramBeta == 0) :
		paramAlfa=paramBeta=1;
		print('errore nei pesi!')
	constSU = sum(paramsW[i]*paramsH[i] for i in setI);
	constHeightSum = sum(paramsH);
	constWidthSum = sum(paramsW);
	constMaxDimensionSum = max(constWidthSum, constHeightSum)
	constMaxPossibleArea = constMaxDimensionSum * constMaxDimensionSum*0 +1*constWidthSum*constHeightSum;
	constMaxFreeSpace = constMaxPossibleArea - constSU;
	constMaxInt = sys.maxsize*0 + 5000000

	I      = [ slv.IntVar([ i ], 'I%d' % i) for i in setI ]
	T      = [ slv.IntVar([ t ], 'T%d' % t) for t in setT ]
	IW     = [ slv.IntVar([ w ], 'IW%d' % i) for i,w in enumerate(paramsW) ]
	IH     = [ slv.IntVar([ h ], 'IH%d' % i) for i,h in enumerate(paramsH) ] # '''enumerate(paramsH)''' ]
	M      = slv.IntVar([ constM ], 'M')
	SU     = slv.IntVar([ constSU ], 'SU')
	alfa   = slv.IntVar([ paramAlfa ], 'alfa')
	beta   = slv.IntVar([ paramBeta ], 'beta')
	#maxInt = slv.IntVar([ constMaxInt ], 'maxInt')


	'''va trovato maxTW e maxTH !!!'''

	# N: se number -> numero fisso; altrimenti maxNumber se presente o constM (UB)
	#N = getNVar('number' in textureOptions, constMaxN, (textureOptions.get('maxNumber', constM)));
	N = getNVar(clamp(int(textureOptions.get('number', 0)), 0, constMaxN), constMaxN);

	# al massimo 1 texture per image => 0<=id<=M-1
	IT = [slv.IntVar(0, constMaxN-1, 'IT%d' % i) for i in setI]
	IX = [slv.IntVar(0, constMaxDimensionSum-paramsW[i], 'IX%d' % i) for i in setI]		# da trovare qual'è la massima X e Y => caso peggiore
	IY = [slv.IntVar(0, constMaxDimensionSum-paramsH[i], 'IY%d' % i) for i in setI]		# in ogni caso si toglie la dimensione ???


	if 'squared' in textureOptions:
		TW = getTextureDims(constMaxDimensionSum, 'TW', ('dimsPowOf2' in textureOptions), setT)
		TH = getTextureDims(constMaxDimensionSum, 'TH', ('dimsPowOf2' in textureOptions), setT)
	else:
		TW = getTextureDims(constWidthSum, 'TW', ('dimsPowOf2' in textureOptions), setT)
		TH = getTextureDims(constHeightSum, 'TH', ('dimsPowOf2' in textureOptions), setT)

	# maxST = massimo spazio totale possibile
	ST = slv.IntVar(0, constMaxPossibleArea, "ST")
	# maxL: maxST-constSU
	L = slv.IntVar(0, constMaxFreeSpace, "L")

	''' 0 < f <= alfa* maxL + beta*M'''
	print('hey', paramAlfa*constMaxInt+paramBeta*constMaxN)
	f = slv.IntVar(0, (paramAlfa*constMaxFreeSpace+paramBeta*constMaxN), "f")


	# BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
	# Signature: Add(<constraint>)
	slv.Add(f == alfa * L + beta * N)

	# CONSTRAINTS
	slv.Add( L == ST - SU)
	slv.Add( ST == slv.Sum([TW[t]*TH[t] for t in setT]))

	slv.Add( N == slv.Max([IT[i] for i in setI])+1)
	#for i in setI:
#		slv.Add( IT[i] < N)

	for t in setT:
		# for each t: if t>=N => tw=0 ^ th=0		(if not used, each dimension IS 0)
		slv.Add( ( T[t] >=N ) <= ( (TW[t]==0)*(TH[t]==0) ))

		# for each t: TW[t]=Max = Max IX[i]+IW[i] for each i, if IT[i]==t 
		slv.Add( TW[t] == slv.Max( [ (IT[i]==t)*(IX[i]+IW[i]) for i in setI] ))
		slv.Add( TH[t] == slv.Max( [ (IT[i]==t)*(IY[i]+IH[i]) for i in setI] ))
		# if options->squared textures 
		if(textureOptions.get('squared', False) == True):	
			slv.Add(TW[t] == TH[t])



	for i in setI:
		for j in setI:
			if i<j:	# i!=j; i<j breaks symmetries! :)
												# < oppure <= ????  (se t=t, almeno un asse non deve sovrapporsi: uno dei due inisce prima dell'altro)
				slv.Add( (IT[i]==IT[j]) <= ( slv.Max( [	(IX[i]+IW[i] < IX[j] ) , ( IX[j]+IW[j] < IX[i])	,
														(IY[i]+IH[i] < IY[j] ) , ( IY[j]+IH[j] < IY[i])	]	) ) )

	#optional constraints
	#squared textures
	#if options.get('squaredTextures', False) == True: 
	#	for t in setT:
	#		slv.Add(TW[t] == TH[t])

	#
	# DEFINE THE SEARCH STRATEGY
	# we will keep this fixed for a few more lectures
	#
	#all_vars = [x1, x2, x3]
	all_vars = I + T + IW + IH + IT + IX + IY + TW + TH + [ M, f, alfa, L, beta, N, ST, SU] #, maxInt];
	#DFS (?) Depth First Search
	#decision_builder = slv.Phase(all_vars, slv.INT_VAR_DEFAULT, slv.INT_VALUE_DEFAULT)


	'''	slv.CHOOSE_FIRST_UNBOUND
		slv.CHOOSE_RANDOM
		slv.CHOOSE_MIN_SIZE_LOWEST_MIN
		slv.CHOOSE_MIN_SIZE_HIGHEST_MIN
		slv.CHOOSE_MIN_SIZE_LOWEST_MAX
		slv.CHOOSE_MIN_SIZE_HIGHEST_MAX
		slv.CHOOSE_LOWEST_MIN
		slv.CHOOSE_HIGHEST_MAX
		slv.CHOOSE_MIN_SIZE
		slv.CHOOSE_MAX_SIZE
		slv.CHOOSE_MAX_REGRET_ON_MIN	'''


	'''	slv.ASSIGN_MIN_VALUE
		slv.ASSIGN_MAX_VALUE
		slv.ASSIGN_RANDOM_VALUE
		slv.ASSIGN_CENTER_VALUE
		slv.SPLIT_LOWER_HALF
		slv.SPLIT_UPPER_HALF	'''



	#decision_builder = slv.Phase(all_vars, slv.CHOOSE_MAX_REGRET_ON_MIN, slv.SPLIT_LOWER_HALF)
	#decision_builder = slv.Phase(all_vars, slv.CHOOSE_MAX_REGRET_ON_MIN, slv.SPLIT_UPPER_HALF)
	decision_builder = slv.Phase(all_vars, slv.CHOOSE_MIN_SIZE_HIGHEST_MAX, slv.ASSIGN_CENTER_VALUE)


	m1 = slv.SearchLog(4*1000*1000) #num_branches
	m2 = None#slv.TimeLimit(    60*1000) #time_limit [milliseconds]
	m3 = slv.Minimize(f, 1)				#  constraint: z <= zbest-step
	# cost function as constraint on variable
	search_monitors = [m1, m2, m3]

	#
	# INIT THE SEARCH PROCESS
	# we will keep this fixed for a few more lectures
	#
	slv.NewSearch(decision_builder ,search_monitors)



	#if slv.solutions() :
	print("ALL variables: ", all_vars)	
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
		if(count%1000==0 or 1):
			sol = '';
			print()
			print('solution %d: ' % count)
			print('variables: ', [ v for v in all_vars if v.Value() != 0])
			print('f: %f' % (f.Value()*1.0/((paramAlfa+paramBeta)/2.0)))
			print('space:\ttotal: %d\t free: %d\t used: %d\nn° of textures: %d' % (ST.Value(), L.Value(), SU.Value(), N.Value()))
			for t in setT:
				if t < N: print('T %d : %d X %d' % (t, TW[t].Value(), TH[t].Value()))
			for i in setI:
				print('I %d : %d in %d,%d [%d x %d]' % (i, IT[i].Value(), IX[i].Value(), IY[i].Value(), IW[i].Value(), IH[i].Value()))
			sol+=str(N.Value())+'\n'
			def getVal(x): return str(x.Value());
			sol+=','.join(map(getVal, TW ))+'\n'
			sol+=','.join(map(getVal, TH ))+'\n'
			sol+=str(constM)+'\n';
			sol+=','.join(map(getVal, IT ))+'\n'
			sol+=','.join(map(getVal, IX ))+'\n'
			sol+=','.join(map(getVal, IY ))+'\n'
			sol+=','.join(map(getVal, IW ))+'\n'
			sol+=','.join(map(getVal, IH ))+'\n'
			print('sol:{\n%s}\n' %sol)
		count+=1

	print()

	#
	# END THE SEARCH PROCESS
	#
	slv.EndSearch()


	print('Total Solutions: %d\nBranches: %d\n Failures: %d\n wall_time: %d' % ( count, slv.Branches(),	slv.Failures(), slv.WallTime()))



if __name__ == "__main__":
	pMain();
