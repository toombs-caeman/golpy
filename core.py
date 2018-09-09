import threading
import time
import numpy as np
"""
This dictionary represents the standard rules of the game of life in the form
(old value, number of neighbors):new value
if a tuple isn't listed it's assumed that the cell is dead
"""
gameoflife = {
	(1, 3):1,
	(1, 2):1,
	(0, 3):1
}
class Core:
	def __init__(this, shape=(40, 40), _gui = None, _rate = 0.1, _ruleset=gameoflife):
		this.gui = _gui
		this.ruleset = _ruleset
		#start paused
		this.running = False
		#set the initial update rate to twice a second
		this.rate = _rate
		# initialize the matrix
		this.matrix = np.matrix(np.zeros(shape, dtype=int))
		#create mutex for writing to matrix
		this.lock = threading.Lock()
		# track the number of iterations since the last clear
		this.itr = 0

	def __str__(this):
		return str(this.matrix)
		
	def setRate(this,_rate):
		#set refresh rate
		this.rate = _rate
		pass

	def pause(this):
		this.running = False

	def play(this):
		if not this.running:
			this.running = True
			threading.Thread(target=this.next).start()
		
	def toggle_play(this):
		this.running = not this.running
		if this.running:
			threading.Thread(target=this.next).start()


	def load(this, point, pattern):
		try:
			this.lock.acquire()
			padx = (point[0],this.matrix.shape[0] - point[0] - pattern.shape[0])
			pady = (point[1],this.matrix.shape[1] - point[1] - pattern.shape[1])
			tmp = this.matrix + np.pad(pattern, (padx, pady), 'constant', constant_values=((0,0),(0,0))) 
			this.matrix = np.matrix(list(map(lambda x : int(x!=0), tmp.flat))).reshape(this.matrix.shape)
		finally:
			this.lock.release()
		if this.gui:
			this.gui.update()
	def resize(this, x, y):
		pass
	def clear(this):
		try:
			this.lock.acquire()
			this.matrix = np.zeros(this.matrix.shape, dtype=int)
			this.itr = 0
		finally:
			this.lock.release()
		

	def next(this):
		try:
			this.lock.acquire()
			startTime = time.time()
			#update the matrix
			# let u equal the sum of the top row of neighbors
			u = np.pad(this.matrix, ((1,1),(0,2)), 'constant')
			u += np.pad(this.matrix, ((2,0),(0,2)), 'constant') + np.pad(this.matrix, (0,2),'constant')
			# let d be the bottom row
			d = np.roll(u, 2, axis=1)
			#let l be the left neighbor
			l = np.pad(this.matrix, ((0,2),(1,1)), 'constant')
			#let r be the right neighbor
			r = np.roll(l, 2, axis=0)
			
			# sum and trim neighbors back to the original size
			neighbors = (u+d+l+r)[1:-1,1:-1]

			# get a list of tuples representing each cell in the form (oldValue, numNeighbors)
			l = zip(this.matrix.flat, neighbors.flat)
			
			# map oldValue, numNeighbors -> newValue according to the current ruleset
			# the default value is 0, or dead
			values = list(map(lambda x:this.ruleset.get(x, 0), l))
			#map (oldValue, numNeighbors) to a new value in 2d and replace the current state
			this.matrix = np.matrix(values).reshape(this.matrix.shape)
			this.itr+= 1
		finally:
			this.lock.release()

		#tell the gui to update
		if this.gui:
			this.gui.update()
		#schedule the next iteration if we're still running
		if this.running:
			elapsed = time.time() - startTime
			threading.Timer(this.rate - elapsed , this.next).start()
	def load_sample(this):
		#load a simple glider
		glider = np.matrix([	[0,1,0],
			  		[0,0,1],
			  		[1,1,1]
					])
		this.load((0,0), glider)
