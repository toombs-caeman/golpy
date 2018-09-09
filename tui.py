import curses
import threading
import sys
import logging
logging.basicConfig(filename='tui.log',level=logging.DEBUG)

from core import Core

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class TUI:
	def inputWorker(self):
		logging.info("input handler thread started")
		commands = {
				'q':self.quit,
				'p':self.core.toggle_play,
				'l':self.core.load_sample,
				'n':self.core.next,
				'h':self.draw_intro
			}
		while self.running:
			# execute the command
			# stdscr.getch blocks until there is input 
			ch = chr(self.stdscr.getch())
			logging.info("got key:%c" % ch)
			commands.get(ch, lambda : None)()

	def draw_intro(this):
		logging.info("printing help screen")
		#draw the introduction/help screen
		this.stdscr.clear()
		this.stdscr.addstr(0, 0, "Hello World!")
		this.stdscr.refresh()

	def update(this):
		logging.info("updating screen")
		this.stdscr.clear()
		height, width = this.stdscr.getmaxyx()
		for row in range(height - 1):
			r = ''.join(list(map(lambda x:' @'[x],this.core.matrix[row,:].flat)))
			this.stdscr.addstr(row, 0, r)

		#TODO print status bar

		# show the new changes
		this.stdscr.refresh()

	def __init__(this, _stdscr):
		this.stdscr = _stdscr
		# initialize the core with the current screen size
		height, width = this.stdscr.getmaxyx()
		this.core = Core(shape=(height - 1, width), _gui=this)
		this.running = True
		this.input = threading.Thread(target=this.inputWorker)
		this.input.start()
		
	def quit(this):
		logging.info("waiting on the worker thread to quit...")
		#clean up resources
		#set flag to false to quit input worker
		this.running = False

def main(stdscr):
	tui = TUI(stdscr)
	tui.input.join()

if __name__== "__main__":
	curses.wrapper(main)
