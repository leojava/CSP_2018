#!/usr/bin/ipython

print ("prova")

# il ; è opzionale --> JavaScript
# format string
''' %d %f %.2f %% '''
a = 'pr %c %s %s %d' % ('L', 'gij', 'g', 15);
print(a)

b = ['k', 156, True, 'rob']		# Lists
print(b[-1])
# b.append(), pot()

c = (1, '2', 'c')	# Tuple (: immutable)
len(b)

d,e = 12,16
f = (1, 2)
f1,f2 = f 

print( d, e, f1 )	# space: separator

a = { 'a': 'gigi'}	# Dictionary: key->value ---> JSON
#ky: any immutable type

#dict.keys(),values(),items(), add(), remove()

# set():	unique elements
# +: list,tuple concatenation
print( 2 in f)      # cerca valori
print( 'gigi' in a) # cerca key

def f1(x = 23):
	return x**2;

lambda t: -t[1]		#nameless f()

'''
True
False
None


and
or
not


\ breaks a line   (there's no need in parentheses )

if:
elif:
else:

1-instruction bodies can stay on the IF line

for x in range(10):
	...

continue
break

enumerate(list) -> (index,item)

range()
zip()


while :

list comprehension



'''




'''
OR_TOOLS

MakeIntVar() --> IntVar()

'''

