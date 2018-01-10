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

	print (data['options'],type(data))


	#
	# CREATE A SOLVER INSTANCE
	# Signature: Solver(<solver name>)
	slv = pywrapcp.Solver('simple-example')

	# CREATE VARIABLES
	# Signature: IntVar(<min>, <max>, [<name>])
	# Alternative signature: IntVar(<domain as a list>, [<name>])
	x1 = slv.IntVar(-2, 5, 'x1')
	x2 = slv.IntVar(-5, 2, 'x2')
	x3 = slv.IntVar(-2, 2, 'x3')
	x3 = slv.IntVar([3], 'x3')


	#
	# BUILD CONSTRAINTS AND ADD THEM TO THE MODEL
	# Signature: Add(<constraint>)
	slv.Add(2 == x1 + x2)

	#
	# DEFINE THE SEARCH STRATEGY
	# we will keep this fixed for a few more lectures
	#
	all_vars = [x1, x2, x3]
	#DFS (?) Depth First Search
	decision_builder = slv.Phase(all_vars,
	                                slv.INT_VAR_DEFAULT,
	                                slv.INT_VALUE_DEFAULT)


	m1 = None #slv.SearchLog(4) #num_branches
	m2 = slv.TimeLimit(3) #time_limit [milliseconds]
	m3 = slv.Minimize(x1, 1)				#  constraint: z <= zbest-step
	# cost function as constraint on variable
	search_monitors = [m1, m2, m3]

	#
	# INIT THE SEARCH PROCESS
	# we will keep this fixed for a few more lectures
	#
	slv.NewSearch(decision_builder ,search_monitors)



	#
	# Enumerate all solutions!
	#
	while slv.NextSolution():
	    # Here, a solution has just been found. Hence, all variables are bound
	    # and their "Value()" method can be called without errors.
	    # The notation %2d prints an integer using always two "spaces"
	    print ('x1: %2d, x2: %2d, x3: %2d' % (x1.Value(), x2.Value(), x3.Value()) )

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
