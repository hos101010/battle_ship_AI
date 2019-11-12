
import ekf #import ship_movement
import board #import Board
import math
import numpy as np

#board 생성, random으로 초기값 셋팅, 적과 아군 정보 생성
grid = board.Board()

print grid.ships[0]
#생성된 아군의 정보와 목표지점 설정
#grid.ships가 아군/ grid.enemies가 적군/ 
#ship_movement(아군정보, 목표지점y,x)

l = grid.ships[0]
obTemp = []
for i in range(grid.aNum - 1) :	#나중에 자기자신은 ob에서 빼줘야함.
	obTemp.append([grid.ships[i+1][0], grid.ships[i+1][1]])	#y,x 좌표만 넣음
for i in range(grid.eNum) :	#나중에 자기자신은 ob에서 빼줘야함.
	obTemp.append([grid.enemies[i][0], grid.enemies[i][1]])	#y,x 좌표만 넣음
"""
l = [38.0, 38.0, math.pi / 8.0, 0.0, 0.0]

obTemp = [[59, 42],[6.0, 7.0], [82,13], [29,141], [66, 142], [38, 156], [15,153]]
ekf.ship_movement(l,58.0, 58.0, obTemp)
"""
#obTemp.append([11.0, 13.0])
ekf.ship_movement(l, grid.ships[0][0] + 20.0, grid.ships[0][1] + 20.0, obTemp)

