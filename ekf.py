
import math
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("../../")
show_animation = True

class Config():
	# simulation parameters
	def __init__(self):
	
		self.max_speed = 2.0 #1.0  # [m/s]
		self.min_speed = -0.5  # [m/s]
		self.max_yawrate = 40.0 * math.pi / 180.0  # [rad/s]
		self.max_accel = 0.4#0.2  # [m/ss]
		self.max_dyawrate = 40.0 * math.pi / 180.0  # [rad/ss]
		self.v_reso = 0.01  # [m/s]
		self.yawrate_reso = 0.1 * math.pi / 180.0  # [rad/s]
		self.dt = 0.1  # [s]
		self.predict_time = 3.0  # [s]
		self.to_goal_cost_gain = 1.0#1.0
		self.speed_cost_gain = 1.0
		self.robot_radius = 1.0 #1.0  # [m]


def motion(x, u, dt):
    # motion model

	x[2] += u[1] * dt
	x[0] += u[0] * math.cos(x[2]) * dt
	x[1] += u[0] * math.sin(x[2]) * dt
	x[3] = u[0]
	x[4] = u[1]

	return x


def calc_dynamic_window(x, config):

    # Dynamic window from robot specification
	#yawrate : 차량이 얼마나 회전했는가
	Vs = [config.min_speed, config.max_speed,
          -config.max_yawrate, config.max_yawrate]

    # Dynamic window from motion model
	Vd = [x[3] - config.max_accel * config.dt,
          x[3] + config.max_accel * config.dt,
          x[4] - config.max_dyawrate * config.dt,
          x[4] + config.max_dyawrate * config.dt]

    #  [vmin,vmax, yawrate min, yawrate max]
	dw = [max(Vs[0], Vd[0]), min(Vs[1], Vd[1]),
          max(Vs[2], Vd[2]), min(Vs[3], Vd[3])]

	return dw


def calc_trajectory(xinit, v, y, config):

	x = np.array(xinit)
	traj = np.array(x) #x가 traj
	time = 0
	while time <= config.predict_time:	
		x = motion(x, [v, y], config.dt)
		traj = np.vstack((traj, x))
		time += config.dt

	return traj


def calc_final_input(x, u, dw, config, goal, ob):

	xinit = x[:]	#임시저장
	min_cost = 100000.0 #초기값
	min_u = u # 초기값 0.0,0.0 -> 갱신
	min_u[0] = 0.0	# [0.0, x]
	best_traj = np.array([x])	#사선 x라고? 계속 갱신되는 배의 위치가 들어감.

    # evalucate all trajectory with sampled input in dynamic window
	#모든 사선 계산
	for v in np.arange(dw[0], dw[1], config.v_reso):	# v - at ~ v + at 사이의 값들, 0.01 간격
		for y in np.arange(dw[2], dw[3], config.yawrate_reso): # 얼마나 회전했는가 회전반경들 
			traj = calc_trajectory(xinit, v, y, config) #그 속도와 각도 별로 경로 계산

			# calc cost
			to_goal_cost = calc_to_goal_cost(traj, goal, config)	#에러 각도 theta2 - theta1
			speed_cost = config.speed_cost_gain * \
				(config.max_speed - traj[-1, 3])
			ob_cost = calc_obstacle_cost(traj, ob, config) #멀수록 값이 작음, 가까우면 커짐
			
			# print(ob_cost)
			# 함선이 움직일 수 있는 범위와 속도 내의 예측 가능 범위 중
			# 목표 지점과의 거리가 가까우면서, (90,45)를 기준으로 각도가 목표 지점에 가까운 방향
			# 그리고, 장애물과의 거리가 먼 곳을 선택해서 움직임
			final_cost = to_goal_cost + speed_cost + ob_cost

			#print (final_cost)

			# search minimum trajectory
			if min_cost >= final_cost:
				#print to_goal_cost, speed_cost, ob_cost
				min_cost = final_cost
				min_u = [v, y]
				best_traj = traj

	return min_u, best_traj


def calc_obstacle_cost(traj, ob, config):
	# calc obstacle cost inf: collision, 0:free

	skip_n = 2
	minr = float("inf")

	for ii in range(0, len(traj[:, 1]), skip_n):
		for i in range(len(ob[:, 0])):
			ox = ob[i, 0]
			oy = ob[i, 1]
			dx = traj[ii, 0] - ox
			dy = traj[ii, 1] - oy

			r = math.sqrt(dx**2 + dy**2)
			if r <= config.robot_radius:
				return float("Inf")  # collision

			if minr >= r:
				minr = r

	return 1.0 / minr  #1.0 / minr  # OK


def calc_to_goal_cost(traj, goal, config):
	# calc to goal cost. It is 2D norm.

	goal_magnitude = math.sqrt((goal[0] - 45)**2 + (goal[1] - 90)**2) #0.0 기준으로의 거리
	traj_magnitude = math.sqrt((traj[-1, 0] - 45)**2 + (traj[-1, 1] - 90)**2) #가장 마지막 예측 지점의 0,0 기준으로부터의 거리
	dot_product = ((goal[0] - 45 )* (traj[-1, 0] - 45)) + ((goal[1] - 90) * (traj[-1, 1]- 90))
	#error는 두 벡터 사이의 내적, 두 벡터 사이 각도 구한 것
	error = dot_product / (goal_magnitude * traj_magnitude)
	error_angle = math.acos(error)
	cost = config.to_goal_cost_gain * error_angle
	dist_magnitude = math.sqrt((goal[0] - traj[-1, 0])**2 + (goal[1] - traj[-1, 1])**2)

	return cost + 0.1*dist_magnitude


def dwa_control(x, u, config, goal, ob):
	# Dynamic Window control

	dw = calc_dynamic_window(x, config)

	u, traj = calc_final_input(x, u, dw, config, goal, ob)

	return u, traj


def plot_arrow(x, y, yaw, length=0.5, width=0.1):  # pragma: no cover
	plt.arrow(x, y, length * math.cos(yaw), length * math.sin(yaw),
              head_length=width, head_width=width)
	plt.plot(x, y)


def ship_movement(clist, gx, gy, obb): #0,0이면 traj_magnitude가 0 돼서 error 계산시 에러남
	
	# initial state [x(m), y(m), yaw(rad), v(m/s), omega(rad/s)]
	#x = np.array([10.0, 10.0, math.pi / 8.0, 0.0, 0.0])
	x = np.array(clist)
	# goal position [x(m), y(m)]
	goal = np.array([gx, gy])
	# obstacles [x(m) y(m), ....]
	"""ob = np.array([[27, 20],
                   [12.0, 12.0]
                   ])
				   """
	ob = np.array(obb)
	print ob
	u = np.array([0.0, 0.0])
	config = Config()
	traj = np.array(x)	#기록용 traj

	for i in range(1000):
		u, ltraj = dwa_control(x, u, config, goal, ob)
		#ltraj ? 
		x = motion(x, u, config.dt)
		traj = np.vstack((traj, x))  # store state history

		# print(traj)

		if show_animation:
			plt.cla()
			plt.plot(ltraj[:, 0], ltraj[:, 1], "-g")
			plt.plot(x[0], x[1], "xr")
			plt.plot(goal[0], goal[1], "xb")
			plt.plot(ob[:, 0], ob[:, 1], "ok")
			plot_arrow(x[0], x[1], x[2])
			plt.axis("equal")
			plt.grid(True)
			plt.pause(0.0001)

        # check goal
		if math.sqrt((x[0] - goal[0])**2 + (x[1] - goal[1])**2) <= config.robot_radius:
			print("Goal!!")
			break

	print("Done")
	if show_animation:
		plt.plot(traj[:, 0], traj[:, 1], "-r")
		plt.pause(0.0001)

	plt.show()

