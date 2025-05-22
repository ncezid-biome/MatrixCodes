#!/usr/bin/python3

import argparse
import json
import os
import sys
import datetime


def getValFromMatrix_BL(key1, key2, matrix):
	"""
	getValFromMatrix_BL:	finds indexes for input keys (key1, key2) in first column of
							bottom-left matrix and uses that to return the value at the
							intersection of key1's row and key2's column
		Arguments:
			key1	--> string; unique sample identifier
			key2	--> string; unique sample identifier, different than key1
			matrix	--> list of lists, first index of each list is string, rest are ints
		Returns:
			int		--> value at interseciton of key1 and key2 in input matrix
		Version:
			1.0
	"""
	idx1 = key1[1]
	idx2 = key2[1]
	if idx1<idx2:
		return matrix[idx2][idx1+1]
	else:
		return matrix[idx1][idx2+1]

def getValFromMatrix_TR(key1, key2, matrix):
	"""
	getValFromMatrix_BL:	finds indexes for input keys (key1, key2) in first column of
							top-right matrix and uses that to return the value at the
							intersection of key1's row and key2's column
		Arguments:
			key1	--> string; unique sample identifier
			key2	--> string; unique sample identifier, different than key1
			matrix	--> list of lists, first index of each list is string, rest are ints
		Returns:
			int		--> value at interseciton of key1 and key2 in input matrix
		Version:
			1.0
	"""
	idx1 = key1[1]
	idx2 = key2[1]
	if idx1<idx2:
		return matrix[idx1][idx2+1]
	else:
		return matrix[idx2][idx1+1]

def setProgressBar(numerator, denominator, totalPoints=20, message=""):
	# progress bar increment, so only totalPoints dots are printed to screen
	progressChunk = int(denominator/totalPoints) if denominator > totalPoints else 1
	nChunks = int(numerator/float(progressChunk))
	# update progress "bar"
	percentComplete = int(float(100*(numerator))/float(denominator))
	if numerator==denominator:
		txt = '{}{}'.format('.'*totalPoints, 
								'100%' if len(message)==0 else '100% ({})'.format(message))

	else:
		txt = '{}{}{}{}'.format('.'*nChunks, 
								' '*(totalPoints-nChunks), 
								percentComplete,
								'%' if len(message)==0 else '% ({})'.format(message))
	sys.stdout.write(txt + '\r')
	sys.stdout.flush()				

def Now():
	"""
	Now:  return current time in yyyy-mm-dd hh:min:ss format
	"""
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class node():
	"""
	node:	parent class to hold codes and child nodes, eventually containing list of sample identifiers
			belonging to exact matches (terminalNodes)
	"""
	def __init__(self, key, thresholds, code, parentCode='', level=0):
		# construct node class to hold input key as founder, recursing with it to fill childNodes
		# until list of thresholds runs out
		self.founder = key
		self.level = level
		self.code = (parentCode + "." + code if len(parentCode) else code)
		self.maxDist = 0
		self.childNodes = {}
		# new nodes have no childNodes, so recurse to add them with code='1'
		if level == len(thresholds)-2:
			self.childNodes.update({'1':terminalNode(key, thresholds, '1', self.code)})
		else:
			self.childNodes.update({'1':node(key, thresholds, '1', self.code, level+1)})
			
	def addChildNode(self, key, thresholds):
		"""
		addChildNode:	creates new node/terminalNode and adds to self.childNodes
			Arguments:
				key			--> string; unique sample id
				thresholds	--> list of floats; distance values to bin samples into different clades
			Returns:
				string		--> next integer value for childNodes converted to string
			Version:
				1.0
		"""
		nextIDX = str(max([int(code) for code in self.childNodes.keys()])+1)
		if self.level<len(thresholds)-2:
			# add new node if not at end of thresholds list
			self.childNodes[nextIDX] = node(key, thresholds, nextIDX, self.code, self.level+1)
		else:
			# otherwise, add new terminalNode
			self.childNodes[nextIDX] = terminalNode(key, thresholds, nextIDX, self.code)
		# return identifier for newly created node for use elsewhere
		return nextIDX
	
	def addMember(self, key, matrix, matrixType, thresholds):
		"""
		addMember:	adds input key to members list (if terminalNode) or evaluates whether
					sample should be added based on input thresholds
			Arguments:
				key			--> string; unique sample id
				matrix		--> list of lists of floats
				matrixType	--> string; 'bl' or 'tr'; used to determine function for extracting distance values from input matrix
				thresholds	--> list of lists of floats
			Version:
				1.0
		"""
		if verbose:
			print('\n\tAdding {} to node {}'.format(key, self.code))
		if isinstance(self, terminalNode):
			# already determined to be part of this node, so add to list
			self.members.append(key)
		else:
			# alias the function for input matrixType
			distFxn = {'bl': getValFromMatrix_BL, 'tr': getValFromMatrix_TR}.get(matrixType)
			# not a terminalNode, so see which childNodes are right for input key
			codeList = []
			nodeList = []
			for code, child in self.childNodes.items():
				# pull out distance to node's founder from input matrix using aliased function
				distVal = distFxn(key, child.founder, matrix)
				if distVal <= thresholds[child.level]:
					# if distance to founder is below threshold, node is a candidate
					codeList.append(code)
					nodeList.append(child)
				elif distVal <= 2*thresholds[child.level] + self.maxDist:
					# if distance to founder is in buffer zone, see if distance to any members fall under threshold
					memberList = child.getMembers()
					if any([distFxn(key, key2, matrix) <= thresholds[child.level] for key2 in memberList]):
						codeList.append(code)
						nodeList.append(child)
			if len(nodeList)==0:
				# no matching nodes below threshold, so add new child node with next consecutive integer
				nextIDX = self.addChildNode(key, thresholds)
			elif len(nodeList)==1:
				# only one matching node, so add key to it
				nodeList[0].addMember(key, matrix, matrixType, thresholds)
			else:
				# more than one node with a match, so merge affected nodes into a new one
				# 1. create new node with this new key as the founder
				nextIDX = self.addChildNode(key, thresholds)
				if verbose:
					print('\nMerging {} into new node ({})...'.format(', '.join(['{} (n={})'.format(node.code, 
																									len(node.getMembers())) for node in nodeList]), 
																		self.childNodes[nextIDX].code))
				# 2. add keys from affected nodes to new node by recursing with this function
				for node in nodeList:
					keyList = node.getMembers()
					for key in keyList:
						self.childNodes[nextIDX].addMember(key, matrix, matrixType, thresholds)
				# 3. remove merged nodes from tree
				for code in codeList:
					del self.childNodes[code]
		# recalculate internal maxDist no matter what happened above
		self.setMaxDist(matrix, matrixType)
		
				
	def getMembers(self):
		"""
		getMembers:	returns list of sample identifiers (if terminalNode) or compiles them into a list (if node)
					for output
			Returns:
				list of strings	--> list of sample identifiers
			Version:
				1.0
		"""
		if isinstance(self, terminalNode):
			# return list of sample identifiers for terminalNode
			return self.members
		else:
			# otherwise, compile list of sample identifiers by recursion
			memberList = []
			for code, child in self.childNodes.items():
				memberList += child.getMembers()
			return memberList
			
	def setMaxDist(self, matrix, matrixType):
		"""
		setMaxDist:	resets the maximum distance between samples within a node to the highest pairwise
					distance for member samples from input matrix
			Arguments:
				matrix		--> list of lists of floats; pairwise distance matrix
				matrixType	--> string; 'bl' or 'tr'; used to determine which function to use for extracting
								distance values from matrix
			Version:
				1.0
		"""
		# get list of sample identifiers
		memberList = self.getMembers()
		# alias the distance function for input matrixType
		distFxn = {'bl': getValFromMatrix_BL, 'tr': getValFromMatrix_TR}.get(matrixType)
		# set maxDist value to max of max of pairwise (non self-self) distances in matrix
		self.maxDist = max([max([distFxn(key1, key2, matrix) for key2 in memberList if key2!=key1]) 
							for key1 in memberList])
		
	def getCodeForKey(self, key):
		"""
		getCodeForKey:	finds most terminalNode containing key with at least one other member and returns
						code for that node
			Arguments:
				key		--> string; unique sample identifier
			Returns:
				string	--> code variable for node containing input key with longest code and at least one other
							sample
			Version:
				1.0
		"""
		# get list of sample identifier for this node
		memberList = self.getMembers()
		# if only one sample, return empty string (i.e  not a match)
		if len(memberList)==1:
			return ""
		else:
			# otherwise, return code if a terminalNode
			if isinstance(self, terminalNode):
				return self.code
			else:
				# or recurse if not
				for child in self.childNodes.values():
					memberList = child.getMembers()
					if key in memberList:
						if len(memberList)>1:
							return child.getCodeForKey(key) 
						else:
							return self.code
							
	def printNode(self):
		"""
		printNode:	outputs tab-indented node contents with tab length equal to level
			Returns:
				string	--> tab-indented node contents
			Version:
				1.0
		"""
		if isinstance(self, terminalNode):
			# return contents of terminalNode with each element on a new line
			return '\n'.join(['\t'*self.level + 'code: %s'%self.code,
							'\t'*self.level + 'level: %d'%self.level, 
							'\t'*self.level + 'founder: %s'%self.founder, 
							'\t'*self.level + 'maxDist: %d'%self.maxDist,
							'\t'*self.level + 'members: %s'%','.join([member[0] for member in self.members])])
		else:
			# return contents of node with each element on a new line and childNodes indented
			# further after recursing back on this function
			return '\n'.join(['\t'*self.level + 'code: %s'%self.code,
							'\t'*self.level + 'level: %d'%self.level, 
							'\t'*self.level + 'founder: %s'%self.founder, 
							'\t'*self.level + 'maxDist: %d'%self.maxDist, 
							'\n'.join([child.printNode() + ('\n' + '\t'*child.level + '='*5 if len(self.childNodes) > 1 else '') for child in self.childNodes.values()])])
					
class terminalNode(node):
	"""
	terminalNode:	child class of node object, containing list of keys which were found at the 0-difference
					threshold (i.e. exact matches) and share the same full-length code
	"""
	def __init__(self, key, thresholds, code, parentCode=''):
		# construct terminalNode with same variables as node parent class, adding "members" list
		# to show keys with exact matches
		self.founder = key
		self.level = len(thresholds)-1
		self.code = (parentCode + "." + code if len(parentCode) else code)
		self.members = [key]
		self.maxDist = 0
	def getMembers(self):
		"""
		getMembers:	returns list of keys belonging to those node
			Returns:
				list of strings	--> list of keys added to this node
		"""
		return self.members
		
class Tree():
	def __init__(self, key):
		# initiate tree with input key, passing to node constructor to auto-fill childNodes with input
		# key as founder
		self.tree = {'1':node(key, thresholds, '1')}
		
	def addNode(self, key, thresholds):
		"""
		addNode:	creates new node, using next highest number, using input key as founder
			Arguments:
				key			--> string; unique sample identifier
				thresholds	--> list of ints; distance thresholds
			Returns:
				int as string	--> next highest node identifier (int) as string
		"""
		# get next highest number for node
		nextIDX = str(max([int(code) for code in self.tree.keys()])+1)
		# add it to tree, using node contstructor, which auto-fills childNodes with input key as founder
		self.tree.update({nextIDX:node(key, thresholds, nextIDX)})
		# return node identifier (nextIDX) for use elsewhere
		return nextIDX
		
	def addToTree(self, key, matrix, matrixType, thresholds):
		"""
		addToTree:	adds input key to appropriate node if below first threshold to founder
					or its members, OR adds it to a new node instead
			Arguments:
				key			--> string; unique sample identifier
				matrix		--> list of lists of floats; distance matrixFile
				matrixType	--> string; 'bl' or 'tr' from user input, 
								denoting bottom-left or top-right matrix, respectively
				thresholds	--> list of ints; discrete integer thresholds, sorted highest to lowest
		"""
		# alias the distance function from input matrixType
		distFxn = {'bl': getValFromMatrix_BL, 'tr': getValFromMatrix_TR}.get(matrixType)
		
		# compile list of nodes to which new sample could belong
		codeList = []
		nodeList = []
		for code, node in self.tree.items():
			# pull out distance to node's founder from in put matrix using aliased function
			distVal = distFxn(key, node.founder, matrix)
			if distVal <= thresholds[0]:
				# if distance to founder is below threshold, node is a candidate
				codeList.append(code)
				nodeList.append(node)
			elif distVal <= 2*thresholds[0] + node.maxDist:
				# if distance to founder is in buffer zone, see if distance to any members fall under threshold
				memberList = node.getMembers()
				if any([distFxn(key, key2, matrix) <= thresholds[0] for key2 in memberList]):
					codeList.append(code)
					nodeList.append(node)
		if len(nodeList)==0:
			# no nodes below first threshold, so add new node to tree with next consecutive integer
			nextIDX = self.addNode(key, thresholds)
		elif len(nodeList)==1:
			# add key to only node compiled
			nodeList[0].addMember(key, matrix, matrixType, thresholds)
		else:
			# more than one node with a match, so merge affected nodes into a new one
			# 1. create new node with this new key as the founder
			nextIDX = self.addNode(key, thresholds)
			# 2. add keys from affected nodes to new node by recursing with this function
			keyList = []
			for node in nodeList:
				keyList = node.getMembers()
				for key in keyList:
					self.tree[nextIDX].addMember(key, matrix, matrixType, thresholds)
			# 3. remove merged nodes from tree
			for code in codeList:
				del self.tree[code]
				
	def getCodeForKey(self, key):
		"""
		getCodeForKey: finds node containing input key, then runs same function on that node
			Arguments:
				key	--> string; unique sample identifier
			Returns:
				string	--> "code" element of node to which input key belongs as long as other
							keys are present (i.e. no singletons); empty string otherwise
		"""
		# find node containing input key
		for code, node in self.tree.items():
			if key in node.getMembers():
				return node.getCodeForKey(key)
		# in case key isn't found
		return ""
		
	def printTree(self):
		"""
		printTree: prints node contents indented according to level
		"""
		return '\n'.join(['\t'*node.level + node.printNode() for node in self.tree.values()])

		
def main():
	global matrix
	global matrixType
	global thresholds
	global verbose
	# get required values from user input
	parser = argparse.ArgumentParser(prog="SNP codes from matrix",
									 description="Code to generate SNP codes from input distance matrix, first column being sample identifiers")
	# matrix file
	parser.add_argument('matrixFile',
						help="Bottom-left (bl) or Top-right (tr) distance matrix with first column being sample identifiers")
	# matrixType
	parser.add_argument('-mt',
						'--matrixType',
						required=True,
						choices=['bl', 'tr'],
						help="'bl' or 'tr', corresponding to bottom-left or top-right type of matrix, respectively")
	# thresholds to use
	parser.add_argument('-t',
						'--thresholds',
						required=True,
						help="Quoted, comma-separated thresholds in descending order")
	# verbosity
	parser.add_argument('-v',
						'--verbose',
						action='store_true',
						help="Whether to print excessively or not")
	
	# validate inputs
	args = parser.parse_args()
	# get matrix as list of lists
	try:
		if args.matrixFile:
			if os.path.exists(args.matrixFile):
				if args.matrixFile.endswith(".csv"):
					delim = ","
				elif args.matrixFile.endswith(".tsv"):
					delim = "\t"
				else:
					delim = " "
				print("{}\tImporting matrix values...".format(Now()))
				with open(args.matrixFile, "r") as m:
					matrix = [row.split(delim) for row in m]
					matrix = [[row[0]] + [float(r) for r in row[1:]] for row in matrix]
			else:
				exit("Matrix file doesn't exist.")
		else:
			exit("Matrix file not provided.")
	except:
		exit("Error reading matrix file.")
	# get user-defined matrix type
	try:
		if args.matrixType:
			matrixType = args.matrixType
		else:
			exit("matrixType not provided")
	except:
		exit("Error processing matrixType")
	# get and sort user-defined distance thresholds
	try:
		if args.thresholds:
			thresholds = list(map(float, args.thresholds.strip().replace(" ", "").split(",")))
			# sort and ensure no negative numbers were given
			thresholds.sort(reverse=True)
			if min(thresholds)<0:
				exit("Negative thresholds not allowed.")
			elif min(thresholds)>0:
				# if zero (i.e. exact match) not provided, add it
				thresholds.append(0)
		else:
			exit("Thresholds not provided")
	except:
		exit("Error parsing thresholds.")
	# see how much user wants to see along the way	
	try:
		if args.verbose:
			verbose = args.verbose
		else:
			verbose = False
	except:
		verbose = False
	
	# pull out sample identifiers with row found in matrix for faster retrieval
	keyList = [[row[0], r] for r, row in enumerate(matrix)]
	
	# Initiate tree with first sample identifier
	tree = Tree(keyList[0])
	
	# Add remaining sample identifiers to tree with provided thresholds
	print('{}: START'.format(Now()))
	
	# tracker for how long each sample took to add to tree
	timeTaken = [Now()]
	
	for k, key in enumerate(keyList[1:]):
		# update progress bar for current sample
		setProgressBar(k+1, 
						len(keyList), 
						message="Adding {}{}".format(key[0], ', avg add time: {}s'.format(sum(timeTaken[-5:-1])/5) if k>=5 else ''))
		# add sample to tree
		tree.addToTree(key, matrix, matrixType, thresholds)
		# add current time to tracker list
		timeTaken.append(Now())
		# update previous time to how long current sample took to add
		timeTaken[-2] = (datetime.datetime.strptime(timeTaken[-1], "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(timeTaken[-2], "%Y-%m-%d %H:%M:%S")).total_seconds()
		
	print('\n{}: END'.format(Now()))
	
	# print blank line to clear progress bar
	print("")
	
	# print resulting codes per sample
	for key in keyList:
		print('{}:\t{}'.format(key[0], tree.getCodeForKey(key)))
	
	# if user chose verbose option, then print tree in tab-indented format
	if verbose:
		print(tree.printTree())

# run code
if __name__=="__main__":
	main()