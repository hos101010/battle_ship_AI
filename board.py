import random
import Tkinter as tk
import time
import numpy as np
import math


class Board:
	
	def __init__(self, visualization=True):
		global WIDTH, HEIGHT, COL_NUM, ROW_NUM, GRID_SIZE

		self.visualization = visualization

		# ========== Board setup ========== #
		GRID_SIZE = 7
		COL_NUM = 180
		ROW_NUM = 90
		WIDTH = GRID_SIZE * COL_NUM
		HEIGHT = GRID_SIZE * ROW_NUM

		# Reset board
		self.board = np.zeros((ROW_NUM, COL_NUM))
		self.saturation_matrix = self.board.copy()
		self.ships = []
		self.enemies = []
		

        # =========== Ship information =========== #
		self.aNum = input("How many ships do you want? ::")
		self.eNum = input("How many enemies? ::")
		
		dist_min = 120
		for i in range(self.aNum):
            # 1: enemy, 2: me
			
			while True : 
				ts = dist_min
				index_y = random.randrange(ROW_NUM)
				index_x = random.randrange(COL_NUM // 4)
				for j in range(len(self.ships)) :
					ts = (index_y - self.ships[j][0])**2 + (index_x - self.ships[j][1])**2
					if ts < dist_min :
						break
				if ts < dist_min :
					continue
				self.board[index_y][index_x] = 2
				self.ships.append([index_y, index_x, math.pi/8.0, 0.0, 0.0])
				break

			
		for i in range(self.eNum):
            # 1: enemy, 2: me
			while True : 
				ts = dist_min
				index_y = random.randrange(ROW_NUM)
				index_x = random.randrange(COL_NUM // 4) + COL_NUM * 3 // 4
				for j in range(len(self.enemies)) :
					ts = (index_y - self.enemies[j][0])**2 + (index_x - self.enemies[j][1])**2
					if ts < dist_min :
						break		
				if ts < dist_min :
					continue		
				self.board[index_y][index_x] = 1
				self.enemies.append([index_y, index_x, math.pi/8.0, 0,0, 0,0])
				break
				
        # ========== Graphics setup ========== #
		if self.visualization:
			self.window = tk.Tk()
			self.window.title("AI with Weapon System")
			self.window.configure(background="white")
			self.canvas = tk.Canvas(self.window, width=WIDTH, height=HEIGHT)
			self.GRID_SIZE = GRID_SIZE
			self.canvas.grid(row=GRID_SIZE, column=GRID_SIZE, columnspan=COL_NUM, rowspan=ROW_NUM)

		self.generate_board()

    # Display board
	def display(self):
		self.window.mainloop()

    # Generate random board
	def generate_board(self):
		if self.visualization:
			self.draw_board()
	
    # Draw board
	def draw_board(self):
        # 1: enemy, 2: me, other: board
		for row in range(ROW_NUM):
			for col in range(COL_NUM):
				if self.board[row][col] == 1:
					color = "red"
				elif self.board[row][col] == 2:
					color = "blue"
				else:
					color = "white"
				
				self.canvas.create_rectangle(col * self.GRID_SIZE, row * self.GRID_SIZE,
                                             (col + 1) * self.GRID_SIZE, (row + 1) * self.GRID_SIZE,
                                             fill=color)
