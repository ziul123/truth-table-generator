"""Print the truth table of a user input expression. Fixed values for propositions can be
set by comma separated <proposition>=<value> pairs.

Symbols
-------
propositions: any letter followed by any combination of letters, numbers and underscores (except "v" or "tmp")
not: the symbol "¬"
and: the symbol "^"
or: the symbol "v"
conditional: the symbol "->"
biconditional: the symbol "<->"

Usage
-----
Binary operations must always be nested in parentheses. For example, "(p v q v r)" must be written
as either "((p v q) v r)" or "(p v (q v r))".
There must always be a space between the symbol of the operation and each of the operands.

Examples
--------
¬p
(p v q)
¬(p -> q)
(p ^ ¬q), p=True
(¬p <-> q), p=True, q=False
"""
###BNF###

# <expr> ::= <prop>|<neg>|<op>
# <prop> ::= "p"|"q"|"r"
# <neg> ::= "¬"<prop>|"¬"<op>
# <op> ::= "("<expr><sym><expr>")"
# <sym> ::= " v "|" ^ "|" -> "|" <-> "

###Tree###
class Expr:
	"""
	Generic expression class.

	Methods
	-------
	eval(env):
		Evaluates the expression.
	"""
	def eval(self,env):
		"""
		Evaluates the expression.

		Paremeters
		----------
		env : dict
			truth values of the propositions.
		"""
		pass


class BinOp(Expr):
	"""
	Generic binary operation class.

	Attributes
	----------
	l : Expr 
		the left operand.
	r : Expr 
		the right operand.
	symbol : str 
		the symbol of the operation.
	"""
	def __init__(self,l,r):
		self.l = l
		self.r = r
		self.symbol = None

	def __str__(self):
		return "(" + str(self.l) + f" {self.symbol} " + str(self.r) + ")"


class UnOp(Expr):
	"""
	Generic unary operation class.

	Attributes
	----------
	r : Expr
		the operand.
	"""
	def __init__(self,r):
		self.r = r


class Prop(Expr):
	"""
	Proposition class.

	Attributes
	----------
	name : str 
		name of the proposition.
	"""
	def __init__(self,name):
		self.name = name

	def __str__(self):
		return self.name

	def eval(self,env):
		return env[self.name]


class Not(UnOp):
	"""
	Not operation.

	Attributes
	----------
	r : Expr
		the operand.
	"""
	def __init__(self,r):
		super().__init__(r)
		self.symbol = "¬"

	def __str__(self):
		return self.symbol + str(self.r)

	def eval(self,env):
		return not self.r.eval(env)


class Conj(BinOp):
	"""
	Conjunction operation.

	Attributes
	----------
	l : Expr 
		the left operand.
	r : Expr 
		the right operand.
	symbol : str 
		symbol for conjunction: '^'.
	"""
	def __init__(self,l,r,symbol = "^"):
		super().__init__(l,r)
		self.symbol = symbol

	def eval(self,env):
		return self.l.eval(env) and self.r.eval(env)


class Disj(BinOp):
	"""
	Disjunction operation.

	Attributes
	----------
	l : Expr 
		the left operand.
	r : Expr 
		the right operand.
	symbol : str 
		symbol for disjunction: 'v'.
	"""
	def __init__(self,l,r,symbol = "v"):
		super().__init__(l,r)
		self.symbol = symbol

	def eval(self,env):
		return self.l.eval(env) or self.r.eval(env)


class Cond(BinOp):
	"""
	Conditional operation.

	Attributes
	----------
	l : Expr 
		the left operand.
	r : Expr 
		the right operand.
	symbol : str 
		symbol for conditional: '->'.
	"""
	def __init__(self,l,r,symbol="->"):
		super().__init__(l,r)
		self.symbol = symbol

	def eval(self,env):
		return (lambda x,y:False if x and not y else True)(self.l.eval(env),self.r.eval(env))


class Bicond(BinOp):
	"""
	Biconditional operation.

	Attributes
	----------
	l : Expr 
		the left operand.
	r : Expr 
		the right operand.
	symbol : str 
		symbol for biconditional: '<->'.
	"""
	def __init__(self,l,r,symbol="<->"):
		super().__init__(l,r)
		self.symbol = symbol

	def eval(self,env):
		return self.l.eval(env) == self.r.eval(env)


###Parser###
import re

prop = re.compile(r"\(?[a-uw-zA-Z][a-uw-zA-Z_0-9]*\)?")
neg = re.compile(r"[ \(]*¬[a-uw-zA-Z\(][a-uw-zA-Z_0-9]*\)?")
disj = re.compile(r" v ")
conj = re.compile(r" \^ ")
cond = re.compile(r" -> ")
bicond = re.compile(r" <-> ")
tmpre = re.compile(r"\(?tmp\)?")
biops = [(disj,Disj),(conj,Conj),(cond,Cond),(bicond,Bicond)]


def paren(str1):
	"""Identify the most nested pair of parenthesis."""
	tmp = ''
	for i in range(str1.find(')'),-1,-1):
		if str1[i] == '(':
			tmp += str1[i]
			break
		tmp += str1[i]
	return tmp[::-1]


def tmp_replace(main,tree):
	"""Replace a tmp node for tree in main ."""
	try:
		if type(main.r) is Prop:
			if main.r.name == "tmp":
				main.r = tree
				return True
	except:
		pass
	try:
		if type(main.r) is Not:
			if main.r.r.name == "tmp":
				main.r.r = tree
				return True
			elif main.r.l.name == "tmp":
				main.r.l = tree
				return True
	except:
		pass
	try:
		if type(main.l) is Not:
			if main.l.r.name == "tmp":
				main.l.r = tree
				return True
			elif main.l.l.name == "tmp":
				main.l.l = tree
				return True
	except:
		pass
	try:
		if type(main.l) is Prop:
			if main.l.name == "tmp":
				main.l = tree
				return True
	except:
		pass
	try:
		if type(main.r.l) is Not:
			if main.r.l.r.name == "tmp":
				main.r.l.r = tree
				return True
	except:
		pass
	return False


def simple(exp):
	"""Parse a single operation enclosed in parentheses."""
	if re.fullmatch(tmpre,exp):
		return Prop("tmp")
	elif re.fullmatch(prop,exp):
		tmp = re.findall(r"[a-uw-zA-Z][a-uw-zA-Z_0-9]*",exp)[0]
		return Prop(tmp)
	elif re.fullmatch(neg,exp):
		tmp = exp.split("¬")[1]
		return Not(simple(tmp))
	else:
		for x in biops:
			if re.search(x[0],exp):
				tmp = re.split(x[0],exp)
				return x[1](simple(tmp[0]),simple(tmp[1]))


def parse(exp,stack=[None]):
	"""Parse an entire expression."""
	tree = stack.pop()
	if paren(exp) == exp:
		if tree:
			tmp = simple(exp)
			tmp_replace(tmp,tree)
			return tmp
		else:
			return simple(exp)
	elif re.fullmatch(r"¬tmp",exp):
		tmp = simple(exp)
		tmp.r = tree
		return tmp
	elif re.fullmatch(prop,exp) or re.fullmatch(neg,exp):
		return simple(exp)
	else:
		tmp = simple(paren(exp))
		if tree:
			flag = tmp_replace(tmp,tree)
			if not flag:
				stack.append(tree)
		stack.append(tmp)
		exp = exp.replace(paren(exp),'tmp')
		result = parse(exp,stack=stack)
		if re.search(r"tmp", str(result)):
			tmp_replace(result,stack.pop())
		return result


###Truth tables###
from itertools import product


def table(expr,assume={}):
	"""
	Prints the truth table of expression expr.

	Parameters
	----------
	expr : Expr
		expression to be evaluated.
	assume : dict
		dictionary of prop:value pairs to be assumed (optional).
	"""
	props = list(set(re.findall(r"[a-uw-zA-Z][a-uw-zA-Z_0-9]*",str(expr))))
	if assume:
		for x in assume:
			try:
				props.remove(x)
			except ValueError:
				print("Proposition not in expression.")
				return
	combs = product([False,True],repeat=len(props))
	final = [list(zip(props, x)) for x in combs]
	if assume:
		for x in final:
			for y,z in assume.items():
				x.append((y,z))
		for x in assume:
			props.append(x)
	dicts = [dict(x) for x in final]
	print(("{:^5} "*len(props)).format(*props),expr,sep='\t')
	for x in dicts:
		print(("{:^5} "*len(props)).format(*map(str,x.values())),expr.eval(x),sep='\t')
	return


if __name__ == '__main__':
	import sys
	try:
		if sys.argv[1] == '-h' or sys.argv[1] == '--help':
			print(__doc__)
	except:
		expr,*values = input("Please enter an expression:\n").split(',')
		if values:
			tmp = [(x.split('=')[0][1:],x.split('=')[1]=="True") for x in values]
			values = dict(tmp)
		try:
			e1 = parse(expr)
			table(e1,values)
		except:
			print("Bad expression.")
