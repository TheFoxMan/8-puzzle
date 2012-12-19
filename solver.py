import sys
import math
import heapq
import copy
from puzzle import Puzzle

#Depth-31 puzzle
#http://w01fe.com/blog/2009/01/the-hardest-eight-puzzle-instances-take-31-moves-to-solve/

#Looked up approach to test for solvability
#http://www.cs.bham.ac.uk/~mdr/teaching/modules04/java2/TilesSolvability.html

#Looked up pseudo-code on A* search algorithm on Wikipedia
#http://en.wikipedia.org/wiki/A*_search_algorithm

#Looked up pseudo-code on Uniform Cost Search on Wikipedia
#http://en.wikipedia.org/wiki/Uniform-cost_search

#Looked up on Stack-Overflow on approaches to solving 8-puzzle
#http://stackoverflow.com/questions/1395513/what-can-be-the-efficient-approach-to-solve-the-8-puzzle-problem

#Gets user input on whether they want to use the
#default puzzle or generate a puzzle of their own
def getUserPuzzleInput():

	#Infinite while loop to keep polling for user input
	#while input values aren't correct
	while True:

		#default puzzle
		user_input = raw_input("Type \"1\" to use a default puzzle, or \"2\" to enter your own puzzle.\n")
		if user_input == '1':
			print "You have chosen the default puzzle.\n"
			puzzle = Puzzle()
			puzzle.printPuzzle()
			return puzzle

		#user-generated puzzle
		elif user_input == '2':
			print "Enter your puzzle, use a zero to represent the blank"

			#Split on each row of input to get rid white spaces and tabs
			puzzle_row_1 = raw_input("Enter the first row, use a space or tabs between numbers    ")
			puzzle_row_1 = puzzle_row_1.split()

			puzzle_row_2 = raw_input("Enter the second row, use a space or tabs between numbers   ")
			puzzle_row_2 = puzzle_row_2.split()

			puzzle_row_3 = raw_input("Enter the third row, use a space or tabs between numbers    ")
			puzzle_row_3 = puzzle_row_3.split()

			#Append the 3 rows of inputs into a list
			#forming a nxn matrix
			puzzle_list = []
			puzzle_list.append(puzzle_row_1)
			puzzle_list.append(puzzle_row_2)
			puzzle_list.append(puzzle_row_3)
			puzzle = Puzzle(puzzle_list)
			puzzle.printPuzzle()
			return puzzle

		else:
			print "Incorrect input, please try again.\n"

#Gets user input on the queueing function
#they wish to use to solve the puzzle
def getUserAlgorithm():

		#Continue polling for user input
		#while input values are not correct
		while True:
			print "\n\nEnter your choice of algorithm"
			print "1. Uniform Cost Search"
			print "2. A* with the Misplaced Tile Heuristic"
			user_input = raw_input("3. A* with the Manhattan distance heuristic\n")

			#For each individual choice, set the queueing_function
			#respectively and return it to be passed in to
			#general search function
			if user_input == '1':
				queueing_function = "UniformCostSearch"
				print "You have chosen Uniform Cost Search \n"
				return queueing_function
			elif user_input == '2':
				queueing_function = "A_star_misplaced"
				print "You have chosen A* with Misplaced Tile Heuristic \n"
				return queueing_function
			elif user_input == '3':
				queueing_function = "A_star_manhattan"
				print "You have chosen A* with Manhattan Distance Heuristic \n"
				return queueing_function

#Calculates misplaced tiles distance
def calcMisplacedTilesDistance(puzzle):
	
	distance = 0

	#For every square not in its goal state location,
	#increment distance by 1
	for i in range(1, puzzle.puzzleSize):
		if puzzle.getPuzzleSquareLocation(i) != puzzle.getGoalSquareLocation(i):
			distance += 1
	return distance

#Calculates manhattan distance
def calcManhattanDistance(puzzle):
	
	distance = 0

	#For every square not in its goal state location,
	#calculate its absolute distance from its goal location
	#based on row distance and column distance
	for value in range(1,puzzle.puzzleSize):
		goal_row_value, goal_col_value = puzzle.getGoalSquareLocation(value)
		puzzle_row_value, puzzle_col_value = puzzle.getPuzzleSquareLocation(value)
		distance += abs( goal_row_value - puzzle_row_value ) + \
								abs( goal_col_value - puzzle_col_value )

	return distance

#Working solvability check
#Calculates solvability of a puzzle in O(1) time
#by calculating inversions
#That is, for every number x in a tile n, calculate
#the number of values that are less than x, but follow
#after x if the matrix is stretched out into a list [1,2,3,4,5,6,7,8,0]

"""
Solvable : Inversion value = even for an odd width puzzle
						or   odd for an even width puzzle
"""						
def checkSolvability(puzzle):
	puzzle_list = []
	inversion_count = 0

	#Get the location of the blank and calculate its index in list format
	blank_row, blank_col = puzzle.getBlankLocation()
	#This is equivalent to its row value * 3 + column value
	#[ x x x ]
	#[ 0 x x ] blank index is 3 in list format
	#[ x x x ] [ x, x, x, 0, x, x, x, x, x]
	blank_index = blank_row*3 + blank_col
	#Convert puzzle matrix to list format
	for i in range(0, puzzle.puzzleWidth):
		puzzle_list += puzzle.startPuzzle[i]

	#For each element index in the puzzle list
	#Count the number of values index2 that are less than index
	#but have a higher index value than index
	for index in range(0, len(puzzle_list)):
		for index2 in range(index+1, len(puzzle_list)):
			#Make sure the current index is not the blank tile
			if index != blank_index:
				if puzzle_list[index2] > puzzle_list[index]:
					inversion_count += 1
	
	#Check for solvability with final inversion count
	if puzzle.puzzleWidth % 2 == 1 and inversion_count % 2 == 0 or\
	puzzle.puzzleWidth % 2 == 0 and inversion_count % 2 == 1:
		return True
	return False

#General search function for solving puzzles
def general_search(problem, queueing_function):

	num_expanded = 0 #Counts number of nodes expanded (excluding root)
	max_nodes_in_queue = 0 #Counts maximum number of nodes in queue
	PQueue = [] #List to be transformed into a priority queue
	visited = {} #Dictionary to keep track of visited nodes (Allows for O(1) searching)
	heapq.heapify(PQueue) #Heapify the list we made earlier
	puzzle = copy.deepcopy(problem) #Make a deep copy just in case so stuff doesn't break

	#Check for solvability in O(1) time
	if not checkSolvability(puzzle):
			print "\nPuzzle is not Solvable!\n"
			return -1

	#If puzzle is solvable, then calculate initial h(n)
	if queueing_function == "UniformCostSearch":
		puzzle.heuristicCost = 0

	elif queueing_function == "A_star_misplaced":
		puzzle.heuristicCost = calcMisplacedTilesDistance(puzzle)

	elif queueing_function == "A_star_manhattan":
		puzzle.heuristicCost = calcManhattanDistance(puzzle)

	#Push initial node onto priority queue
	heapq.heappush(PQueue,puzzle)

	#While queue is not empty
	#Values still exist in the queue which means search has not
	#been exhausted(backup in case solvability check fails)
	while len(PQueue) != 0:

		#Pop the node with lowest total cost from queue
		#(Overloaded <= operator in puzzle class)
		prevPuzzle = heapq.heappop(PQueue)

		#Check if the puzzle's state is equivalent to the goal state
		if prevPuzzle.checkIfFinished():
			#If true print out completion and the trace
			#for nodes expanded and maximum nodes in queue
			print "\nGoal!!"
			prevPuzzle.printPuzzle()
			print "\nTo solve this problem the search algorithm expanded a total of", num_expanded, "nodes."
			print "The maximum number of nodes in the queue at any one time was", max_nodes_in_queue,"."
			print "The depth of the goal node was", prevPuzzle.depth , "."
			return

		#Otherwise, print out trace for next best node to expand
		print "\nThe best state to expand with a g(n) =",prevPuzzle.depth\
					,"and h(n) =",prevPuzzle.heuristicCost,"is..."

		#Print out the node that we are expanding
		prevPuzzle.printPuzzle()
		print "\nExpanding this node..."

		#Generate all possible moves(children) for that node
		puzzle_tree = prevPuzzle.GenerateMoves()

		#For all the children of the current node popped
		for puzzle in puzzle_tree:

			#Generate a list and then convert it into a string
			#based off the puzzle's state
			#This will be our key in our dictionary for hashing
			puzzle_list = []
			for list in puzzle.startPuzzle:
				puzzle_list += list
			puzzle_key = ""
			for elem in puzzle_list:
				puzzle_key += str(elem)

			#If the key does not exist in our dictionary
			if puzzle_key not in visited:

				#Hash in the new node with its respective key
				#Must convert to tuple since lists are not hashable
				visited[puzzle_key] = tuple(puzzle_list)

				#Create the new puzzle to be pushed onto queue
				#and calculate its respective h(n) value
				nextPuzzle = Puzzle(puzzle.startPuzzle)
				if queueing_function == "UniformCostSearch":
					nextPuzzle.heuristicCost = 0
				elif queueing_function == "A_star_misplaced":
					nextPuzzle.heuristicCost = calcMisplacedTilesDistance(nextPuzzle)
				elif queueing_function == "A_star_manhattan":
					nextPuzzle.heuristicCost = calcManhattanDistance(nextPuzzle)

				#Increment depth counter for children
				nextPuzzle.depth = prevPuzzle.depth+1
				#Push child onto priority queue
				heapq.heappush(PQueue,nextPuzzle)
				#Increment number of nodes expanded
				num_expanded += 1

			#If the current number of nodes in queue exceeds
			#current maximum counter, update maximum
			if len(PQueue) > max_nodes_in_queue:
				max_nodes_in_queue = len(PQueue)

	#Return failure if 2nd check trips
	#(Should not happen because solvability check should handle)
	print "This puzzle is not solvable! \n"
	return -1

#Main block
def main():
	#Fetch user parameters
	puzzle = getUserPuzzleInput()
	queueing_function = getUserAlgorithm()
	#Pass parameters and call search
	general_search(puzzle, queueing_function)

#Boiler-plate
if __name__ == "__main__":
	main()