#-*- coding:utf-8 -*-
import ekf #import ship_movement
import board_sy #import Board
import math
import matplotlib.pyplot as plt
import numpy as np
import logging

class Game:
    def __init__(self):
        #grid_set = GridSet()
        
        #game클리스 들어가면 현재 플레이어는 1이 됨
        self.currentPlayer = 1
        
        #gamestate를 설정해줌 gamestate클래스로 기기
        self.gameState = GameState(np.zeros(16200), 1) #1: player turn
        
        self.actionSpace = np.zeros(16200)
        self.pieces = {'1':'X', '0':'-', '-1':'O'}
        self.grid_shape = (90,180)
        self.input_shpae = (2,90,180)
        self.name = 'battleship'
        self.state_size = len(self.gameState.binary)    #binary는 내경기(len(board)에서 1,0반영) + 상대방 경기(len(board)에서 -1,0반영)  --> 42*2
        self.action_size = len(self.actionSpace)        #42*2
        
    def reset(self):
        self.gameState = GameState(zeros(16200), 1)
        self.currentPlayer = 1
        return self.gameState
        
    def step(self, action):
        next_state, value, done = self.gameState.takeAction(action)     #action정해서 takeaction함수 호출      졌으면 -1, 아니면 0
        self.gameState = next_state                                     #gamestate에 step 반영
        self.currentPlayer = -self.currentPlayer                        #턴 넘겨줌
        info = None
        return ((next_state, value, done, info))
        
        
    #identities는 아직안고침
    def identities(self, state, actionValues):
        identities = [(state,actionValues)]
        
        currentBoard = state.board
        currentAV = actionValues
        
        currentBoard = np.array([
            currentBoard[6], currentBoard[5], currentBoard[4], currentBoard[3], currentBoard[2], currentBoard[1], currentBoard[0]
            , currentBoard[13], currentBoard[12], currentBoard[11], currentBoard[10], currentBoard[9], currentBoard[8], currentBoard[7]
            , currentBoard[20], currentBoard[19], currentBoard[18], currentBoard[17], currentBoard[16], currentBoard[15], currentBoard[14]
            , currentBoard[27], currentBoard[26], currentBoard[25], currentBoard[24], currentBoard[23], currentBoard[22], currentBoard[21]
            , currentBoard[34], currentBoard[33], currentBoard[32], currentBoard[31], currentBoard[30], currentBoard[29], currentBoard[28]
            , currentBoard[41], currentBoard[40], currentBoard[39], currentBoard[38], currentBoard[37], currentBoard[36], currentBoard[35]
            ])
            
        currentAV = np.array([
            currentAV[6], currentAV[5], currentAV[4], currentAV[3], currentAV[2], currentAV[1], currentAV[0]
            , currentAV[13], currentAV[12], currentAV[11], currentAV[10], currentAV[9], currentAV[8], currentAV[7]
            , currentAV[20], currentAV[19], currentAV[18], currentAV[17], currentAV[16], currentAV[15], currentAV[14]
            , currentAV[27], currentAV[26], currentAV[25], currentAV[24], currentAV[23], currentAV[22], currentAV[21]
            , currentAV[34], currentAV[33], currentAV[32], currentAV[31], currentAV[30], currentAV[29], currentAV[28]
            , currentAV[41], currentAV[40], currentAV[39], currentAV[38], currentAV[37], currentAV[36], currentAV[35]
            ])
            
        identities.append((GameState(currentBoard, state.playerTurn), currentAV))
        
        return identities
            
        
        
class GameState():
    def __init__(self, board, playerTurn):  #board는 0으로 세팅, playerturn은 1로 세팅
        self.board = board  #board를 0으로 6*7짜리로 세팅
        self.pieces = {'1':'X', '0':'-', '-1':'O'}
        self.winners = [    #이기는 상황 리스트로 저장
            
			[15,23,31,39],
			[14,22,30,38],
			]
            
        self.playerTurn = playerTurn    #playerturn을 1로 세팅
        self.binary = self._binary()    #첫 요소 : 보드의 1,0(나) // 두번째 요소 : 보드의 -1,0(상대방)        **playerturn변수 이용
        self.id = self._convertStateToId()  #binary를 str으로 나열  but, playerturn사용안하고 첫요소는 무조건 1, 뒷요소는 -1로 판단
        
        #allowed 모르겠음
        self.allowedActions = self._allowedActions()    #마지막줄에있는 아무것도 안놓여있는칸들 + 마지막이 아닌것중에 돌이 안놓여져있고 밑에칸에는 놓여져있는것들
        self.isEndGame = self._checkForEndGame()    #판이 꽉차거나 지면 1 아니면 0
        self.value = self._getValue()               #졌으면 (-1,-1,1) 아니면(0,0,0)
        self.score = self._getScore()               #졌으면 (-1,1) 아니면 (0,0)
        
    def _allowedActions(self):
        allowed = []
        for i in range(len(self.board)):    #보드의 배열 하나씩 for문으로 돌리넹
            if i >= len(self.board) - 7 :   #만약 보드의 몇번째가 보드의 길이빼기 7보다 크면   --> 42-7=35 --> 마지막줄이면
                if self.board[i]==0:        #마지막줄에있는 요소가 0이면
                    allowed.append(i)       #allowed에 추가
            else:                           #마지막줄이 아니면    
                if self.board[i] == 0 and self.board[i+7] != 0:     #board가 0이고(아무것도 안놓아져있고) 그 밑에줄이 0이 아니면(돌이 놓아져있으면)
                    allowed.append(i)                               #allowed에 추가
                    
        return allowed      #마지막줄의 요소 중에 0인것(돌이 안놓여져있는것)  +  마지막이 아닌것중에 0인고 바로 밑에칸이 0이 아닌것
        
        
    def _binary(self):
        currentplayer_position = np.zeros(len(self.board), dtype=np.int)    #current player position을 다 0으로 설정
        currentplayer_position[self.board==self.playerTurn] = 1             #만약 board에 1인게 있다면 position을 1로 설정. 즉 current position이 보드의 1,0을 반영
        
        other_position = np.zeros(len(self.board), dtype=np.int)            #other position을 다 0으로 설정
        other_position[self.board==-self.playerTurn] = 1                    #board에 -1인게 있다면 other position을 1로 설정. 즉 other position이 보드의 -1,0을 반영
        
        position = np.append(currentplayer_position, other_position)        #position은 [current, other]
        
        return (position)
        
        
    def _convertStateToId(self):
        player1_position = np.zeros(len(self.board), dtype=np.int)
        player1_position[self.board==1] = 1
        
        other_position = np.zeros(len(self.board), dtype=np.int)
        other_position[self.board==-1] = 1
        
        position = np.append(player1_position, other_position)
        
        id = ''.join(map(str,position))
        #id는 position을 쭉 합친 str
        #0000000 0000000 0000000 0000000 0000000 0000000 // 0000000 0000000 0000000 0000000 0000000 0000000
        
        return id
        
        
        
    def _checkForEndGame(self):
        #게임 끝났는지 확인
        #전투함이 다 없어졌으면 끝
        
        grid_set= GridSet()
        if len(grid_set.battle.ships) == 0:
            return 1        #짐
        
        if len(grid_set.battle.enemies) == 0:
            return 1        #이김
            
        return 0    #아직 끝나지 않음
        
        
        ######################이기고 진거 구별할 필요 있음!!
        
        '''
        if np.count_nonzero(self.board) == 42:      #돌이 빈곳이 없이 다 차있으면 게임끝
            return 1
            
        for x,y,z,a in self.winners:                #이기는 경우의 수 다 돌림 ex)14 22 30 38 // 3 4 5 6
            if (self.board[x] + self.board[y] + self.board[z] + self.board[a] == 4 * -self.playerTurn): #다 더하면 -4라는 이야기는 졌다는 것
                return 1
            return 0    #0이면 게임 아직 끝나지 않았다 (이겼는지는 판단x)
        '''
        
    def _getValue(self):
        #현재 플레이어의 상태에 대한 값
        #만약 그 전 플레이어가 이기는 움직임이 있었다면 진다.
        for x,y,z,a in self.winners:
            if (self.board[x] + self.board[y] + self.board[z] + self.board[a] == 4 * -self.playerTurn):
                return (-1, -1, 1)
            return (0, 0, 0)
        
    def _getScore(self):
        tmp = self.value
        return (tmp[1], tmp[2]) #졌으면 (-1,1) 아니면 (0,0)
        
    def takeAction(self, action):                           #action은 돌의 위치
        newBoard = np.array(self.board)                     #board생성
        newBoard[action] = self.playerTurn                  #action값을 playerturn으로(1)
        
        newState = GameState(newBoard, -self.playerTurn)    #action반영하고 상대방한테 턴 넘기기
        
        value = 0
        done = 0
        
        if newState.isEndGame:
            value = newState.value[0]                       #졌으면 ("-1",-1,1) 아니면("0",0,0)
            done = 1
        return (newState, value, done)                      #(현재 게임 진행상황 , 졌으면-1,아니면0 , 1)
        
        
    def render(self, logger):
        for r in range(6):
            logger.info([self.pieces[str(x)] for x in self.board[7*r : (7*r + 7)]])
        logger.info('----------------')
        
        

class GridSet() :
    def __init__(self):
        self.battle = board_sy.Board()   #보드 불러옴
        self.goal = [45,90]          #이게 내가 가고자하는 위치로 설정한건강???
        self.grid_update(self.battle, self.goal)
        self.grid_display()
        
        #여기까지가 초기에 그리드 보여주는 것
        
        #첫번째 함선 위치 프린트
        print self.battle.ships[0]
        

        self.traj=self.movement_update(self.battle, self.goal)
        self.grid_update_2(self.battle, self.goal, self.traj)
        self.grid_display()
    
    def grid_init(self) :
        plt.cla()
        plt.rcParams["figure.figsize"] =(16,8)
        self.ax = plt.subplot(111)

        plt.xlim([0, 180])
        plt.ylim([0, 90])
        plt.grid(True)
                
        plt.xticks([i for i in range(0,180)])
        plt.yticks([i for i in range(0,90)]) #i for i in range(0,90)
        plt.grid(color='#BDBDBD', linestyle='-', linewidth=1, )
        return self.ax

    def plot_arrow(self, x, y, yaw, length=0.5, width=0.1):  # pragma: no cover
        plt.arrow(x, y, length * math.cos(yaw), length * math.sin(yaw),
                  head_length=width, head_width=width)
        plt.plot(x, y)


    def grid_display(self) :
        plt.show()

    def grid_update(self, battle, goal) :
        self.ax = self.grid_init()    #새로운 그리드
        self.mRange = 7	#missile Range
        
        #원 그리기
        for i in range(battle.aNum) :
            plt.plot(battle.ships[i][1], battle.ships[i][0], "xb")
            self.plot_arrow(battle.ships[i][1], battle.ships[i][0], battle.ships[i][2])
            c = plt.Circle((battle.ships[i][1], battle.ships[i][0]), self.mRange, fc = 'w', ec = 'b')
            self.ax.add_patch(c)
        
        for i in range(battle.eNum) :
            plt.plot(battle.enemies[i][1], battle.enemies[i][0], "xr")
            self.plot_arrow(battle.enemies[i][1], battle.enemies[i][0], battle.enemies[i][2])
            c = plt.Circle((battle.enemies[i][1], battle.enemies[i][0]), self.mRange, fc = 'w', ec = 'r')
            self.ax.add_patch(c)

    def grid_update_2(self, battle, goal, traj) :
        self.ax = self.grid_init()
        self.mRange = 7	#missile Range
        
        for i in range(battle.aNum) :
            plt.plot(battle.ships[i][1], battle.ships[i][0], "xb")
            self.plot_arrow(battle.ships[i][1], battle.ships[i][0], battle.ships[i][2])
            c = plt.Circle((battle.ships[i][1], battle.ships[i][0]), self.mRange, fc = 'w', ec = 'b')
            self.ax.add_patch(c)
        
        for i in range(battle.eNum) :
            plt.plot(battle.enemies[i][1], battle.enemies[i][0], "xr")
            self.plot_arrow(battle.enemies[i][1], battle.enemies[i][0], battle.enemies[i][2])
            c = plt.Circle((battle.enemies[i][1], battle.enemies[i][0]), self.mRange, fc = 'w', ec = 'r')
            self.ax.add_patch(c)
        
        plt.plot(traj[:, 1], traj[:, 0], "-k")  #이동경로 출력


    def movement_update(self, battle, goal):
        obTemp = []
        for i in range(battle.aNum - 1) :
            obTemp.append([battle.ships[i+1][0], battle.ships[i+1][1]])
        for i in range(battle.eNum) :
            obTemp.append([battle.enemies[i][0], battle.enemies[i][1]])
            
        #여기까지 obTemp에 움직일 것 빼고 다 넣음
        
        print("obTemp에 다 넣음-ja")
        traj, battle.ships[0] = ekf.ship_movement(battle.ships[0], 45, 90, obTemp)  #여기서 움직이는거 다 출력됨
        print("0번째 함선 출력할거임-ja")
        print battle.ships[0]
        return traj


####################여기까지##################    
b=Game()
print(b.action_size)