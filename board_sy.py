import random
import Tkinter as tk
import time
import numpy as np
import math
import matplotlib.pyplot as plt
from pylab import figure, show

def plot_arrow(x, y, yaw, length=0.5, width=0.1):  # pragma: no cover
		plt.arrow(x, y, length * math.cos(yaw), length * math.sin(yaw),
				  head_length=width, head_width=width)
		plt.plot(x, y)

class Board:
	
		
	def __init__(self, visualization=True):
		global WIDTH, HEIGHT, COL_NUM, ROW_NUM, GRID_SIZE

		self.visualization = visualization
		plt.cla()
		plt.rcParams["figure.figsize"] = (16,8)
		ax = plt.subplot(111)
		# ========== Board setup ========== #
		GRID_SIZE = 7
		COL_NUM = 180
		ROW_NUM = 90
		WIDTH = GRID_SIZE * COL_NUM
		HEIGHT = GRID_SIZE * ROW_NUM
		
		#=========== Variables ============ #
		dist_min = 110	#함선끼리 떨어져 있는 min 거리
		mRange = 7	#missile Range
		

		# Reset board
		self.board = np.zeros((ROW_NUM, COL_NUM))
		self.saturation_matrix = self.board.copy()
		self.ships = []
		self.enemies = []
		

        # =========== Ship information =========== #
		self.aNum = input("How many ships do you want? ::")
		self.eNum = input("How many enemies? ::")
		
		#여기는 함선이 너무 따닥따닥 붙어있어서 경로 겹치는 것을 방지하고자 만든 곳임.
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
				#이부분이 배 위치 저장하는 곳
				#index_y, index_x가 좌표, math_pi/8.0 방향, 속동, 각속도
				#진아님이 배 정보를 추가하고 싶다면 append에서 [] 안에 컬럼 하나 넣어주면 됩니당
				self.board[index_y][index_x] = 2
				self.ships.append([index_y, index_x, math.pi/8.0, 0.0, 0.0])
				#grid에 추구하는 부분
				plt.plot(index_x, index_y, "xb")	#점 표시
				plot_arrow(index_x, index_y, math.pi/8.0)	#화살표 표시
				c = plt.Circle((index_x, index_y), mRange, fc = 'w', ec = 'b')
				ax.add_patch(c)
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
				#이부분이 적군 위치 저장하는 곳
				#index_y, index_x가 좌표, math_pi/8.0 방향, 속동, 각속도
				#진아님이 배 정보를 추가하고 싶다면 append에서 [] 안에 컬럼 하나 넣어주면 됩니당
				self.board[index_y][index_x] = 1
				self.enemies.append([index_y, index_x, math.pi/8.0, 0,0, 0,0])
				plt.plot(index_x, index_y, "xr")
				plot_arrow(index_x, index_y, math.pi/8.0)
				c = plt.Circle((index_x, index_y), mRange, fc = 'w', ec = 'r')
				ax.add_patch(c)
				break
		
        # ========== Graphics setup ========== #
		if self.visualization:
			"""self.window = tk.Tk()

			self.window.title("AI with Weapon System")
			self.window.configure(background="white")
			self.canvas = tk.Canvas(self.window, width=WIDTH, height=HEIGHT)
			self.GRID_SIZE = GRID_SIZE
			self.canvas.grid(row=GRID_SIZE, column=GRID_SIZE, columnspan=COL_NUM, rowspan=ROW_NUM)
"""
			#fig = plt.figure(figsize=(50,100))
			#fig.add_subplot(1, 1, 1)
			plt.xlim([0, 180])
			plt.ylim([0, 90])
			plt.grid(True)
			
			plt.xticks([i for i in range(0,180)])
			plt.yticks([i for i in range(0,90)]) #i for i in range(0,90)
			plt.grid(color='#BDBDBD', linestyle='-', linewidth=1, )
			
			
		plt.show()
	
	
		
    # Display board
	def display(self):
		#self.window.mainloop()
		plt.show()
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

grid = Board()
grid.display()