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
        
        #gameŬ���� ���� ���� �÷��̾�� 1�� ��
        self.currentPlayer = 1
        
        #gamestate�� �������� gamestateŬ������ ���
        self.gameState = GameState(np.zeros(16200), 1) #1: player turn
        
        self.actionSpace = np.zeros(16200)
        self.pieces = {'1':'X', '0':'-', '-1':'O'}
        self.grid_shape = (90,180)
        self.input_shpae = (2,90,180)
        self.name = 'battleship'
        self.state_size = len(self.gameState.binary)    #binary�� �����(len(board)���� 1,0�ݿ�) + ���� ���(len(board)���� -1,0�ݿ�)  --> 42*2
        self.action_size = len(self.actionSpace)        #42*2
        
    def reset(self):
        self.gameState = GameState(zeros(16200), 1)
        self.currentPlayer = 1
        return self.gameState
        
    def step(self, action):
        next_state, value, done = self.gameState.takeAction(action)     #action���ؼ� takeaction�Լ� ȣ��      ������ -1, �ƴϸ� 0
        self.gameState = next_state                                     #gamestate�� step �ݿ�
        self.currentPlayer = -self.currentPlayer                        #�� �Ѱ���
        info = None
        return ((next_state, value, done, info))
        
        
    #identities�� �����Ȱ�ħ
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
    def __init__(self, board, playerTurn):  #board�� 0���� ����, playerturn�� 1�� ����
        self.board = board  #board�� 0���� 6*7¥���� ����
        self.pieces = {'1':'X', '0':'-', '-1':'O'}
        self.winners = [    #�̱�� ��Ȳ ����Ʈ�� ����
            
			[15,23,31,39],
			[14,22,30,38],
			]
            
        self.playerTurn = playerTurn    #playerturn�� 1�� ����
        self.binary = self._binary()    #ù ��� : ������ 1,0(��) // �ι�° ��� : ������ -1,0(����)        **playerturn���� �̿�
        self.id = self._convertStateToId()  #binary�� str���� ����  but, playerturn�����ϰ� ù��Ҵ� ������ 1, �޿�Ҵ� -1�� �Ǵ�
        
        #allowed �𸣰���
        self.allowedActions = self._allowedActions()    #�������ٿ��ִ� �ƹ��͵� �ȳ����ִ�ĭ�� + �������� �ƴѰ��߿� ���� �ȳ������ְ� �ؿ�ĭ���� �������ִ°͵�
        self.isEndGame = self._checkForEndGame()    #���� �����ų� ���� 1 �ƴϸ� 0
        self.value = self._getValue()               #������ (-1,-1,1) �ƴϸ�(0,0,0)
        self.score = self._getScore()               #������ (-1,1) �ƴϸ� (0,0)
        
    def _allowedActions(self):
        allowed = []
        for i in range(len(self.board)):    #������ �迭 �ϳ��� for������ ������
            if i >= len(self.board) - 7 :   #���� ������ ���°�� ������ ���̻��� 7���� ũ��   --> 42-7=35 --> ���������̸�
                if self.board[i]==0:        #�������ٿ��ִ� ��Ұ� 0�̸�
                    allowed.append(i)       #allowed�� �߰�
            else:                           #���������� �ƴϸ�    
                if self.board[i] == 0 and self.board[i+7] != 0:     #board�� 0�̰�(�ƹ��͵� �ȳ������ְ�) �� �ؿ����� 0�� �ƴϸ�(���� ������������)
                    allowed.append(i)                               #allowed�� �߰�
                    
        return allowed      #���������� ��� �߿� 0�ΰ�(���� �ȳ������ִ°�)  +  �������� �ƴѰ��߿� 0�ΰ� �ٷ� �ؿ�ĭ�� 0�� �ƴѰ�
        
        
    def _binary(self):
        currentplayer_position = np.zeros(len(self.board), dtype=np.int)    #current player position�� �� 0���� ����
        currentplayer_position[self.board==self.playerTurn] = 1             #���� board�� 1�ΰ� �ִٸ� position�� 1�� ����. �� current position�� ������ 1,0�� �ݿ�
        
        other_position = np.zeros(len(self.board), dtype=np.int)            #other position�� �� 0���� ����
        other_position[self.board==-self.playerTurn] = 1                    #board�� -1�ΰ� �ִٸ� other position�� 1�� ����. �� other position�� ������ -1,0�� �ݿ�
        
        position = np.append(currentplayer_position, other_position)        #position�� [current, other]
        
        return (position)
        
        
    def _convertStateToId(self):
        player1_position = np.zeros(len(self.board), dtype=np.int)
        player1_position[self.board==1] = 1
        
        other_position = np.zeros(len(self.board), dtype=np.int)
        other_position[self.board==-1] = 1
        
        position = np.append(player1_position, other_position)
        
        id = ''.join(map(str,position))
        #id�� position�� �� ��ģ str
        #0000000 0000000 0000000 0000000 0000000 0000000 // 0000000 0000000 0000000 0000000 0000000 0000000
        
        return id
        
        
        
    def _checkForEndGame(self):
        #���� �������� Ȯ��
        #�������� �� ���������� ��
        
        grid_set= GridSet()
        if len(grid_set.battle.ships) == 0:
            return 1        #��
        
        if len(grid_set.battle.enemies) == 0:
            return 1        #�̱�
            
        return 0    #���� ������ ����
        
        
        ######################�̱�� ���� ������ �ʿ� ����!!
        
        '''
        if np.count_nonzero(self.board) == 42:      #���� ����� ���� �� �������� ���ӳ�
            return 1
            
        for x,y,z,a in self.winners:                #�̱�� ����� �� �� ���� ex)14 22 30 38 // 3 4 5 6
            if (self.board[x] + self.board[y] + self.board[z] + self.board[a] == 4 * -self.playerTurn): #�� ���ϸ� -4��� �̾߱�� ���ٴ� ��
                return 1
            return 0    #0�̸� ���� ���� ������ �ʾҴ� (�̰������ �Ǵ�x)
        '''
        
    def _getValue(self):
        #���� �÷��̾��� ���¿� ���� ��
        #���� �� �� �÷��̾ �̱�� �������� �־��ٸ� ����.
        for x,y,z,a in self.winners:
            if (self.board[x] + self.board[y] + self.board[z] + self.board[a] == 4 * -self.playerTurn):
                return (-1, -1, 1)
            return (0, 0, 0)
        
    def _getScore(self):
        tmp = self.value
        return (tmp[1], tmp[2]) #������ (-1,1) �ƴϸ� (0,0)
        
    def takeAction(self, action):                           #action�� ���� ��ġ
        newBoard = np.array(self.board)                     #board����
        newBoard[action] = self.playerTurn                  #action���� playerturn����(1)
        
        newState = GameState(newBoard, -self.playerTurn)    #action�ݿ��ϰ� �������� �� �ѱ��
        
        value = 0
        done = 0
        
        if newState.isEndGame:
            value = newState.value[0]                       #������ ("-1",-1,1) �ƴϸ�("0",0,0)
            done = 1
        return (newState, value, done)                      #(���� ���� �����Ȳ , ������-1,�ƴϸ�0 , 1)
        
        
    def render(self, logger):
        for r in range(6):
            logger.info([self.pieces[str(x)] for x in self.board[7*r : (7*r + 7)]])
        logger.info('----------------')
        
        

class GridSet() :
    def __init__(self):
        self.battle = board_sy.Board()   #���� �ҷ���
        self.goal = [45,90]          #�̰� ���� �������ϴ� ��ġ�� �����Ѱǰ�???
        self.grid_update(self.battle, self.goal)
        self.grid_display()
        
        #��������� �ʱ⿡ �׸��� �����ִ� ��
        
        #ù��° �Լ� ��ġ ����Ʈ
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
        self.ax = self.grid_init()    #���ο� �׸���
        self.mRange = 7	#missile Range
        
        #�� �׸���
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
        
        plt.plot(traj[:, 1], traj[:, 0], "-k")  #�̵���� ���


    def movement_update(self, battle, goal):
        obTemp = []
        for i in range(battle.aNum - 1) :
            obTemp.append([battle.ships[i+1][0], battle.ships[i+1][1]])
        for i in range(battle.eNum) :
            obTemp.append([battle.enemies[i][0], battle.enemies[i][1]])
            
        #������� obTemp�� ������ �� ���� �� ����
        
        print("obTemp�� �� ����-ja")
        traj, battle.ships[0] = ekf.ship_movement(battle.ships[0], 45, 90, obTemp)  #���⼭ �����̴°� �� ��µ�
        print("0��° �Լ� ����Ұ���-ja")
        print battle.ships[0]
        return traj


####################�������##################    
b=Game()
print(b.action_size)