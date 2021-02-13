"""
Benchmark reinforcement learning (RL) algorithms from Stable Baselines 2.10.
Author: Gargi Vaidya & Vishnu Saj
- Note : Modify the state & action space as well as reward function for specific goal.

"""
import gym
import numpy as np
import random
import math
import csv
from gym import spaces
from stable_baselines.common.env_checker import check_env
from subprocess import PIPE, Popen
from threading  import Thread
import sys
import numpy as np
import re
from queue import Queue, Empty, LifoQueue
import olympe
from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, Landing,moveTo, PCMD
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged, AttitudeChanged, moveByChanged, AltitudeChanged, GpsLocationChanged

class ParrotEnv(gym.Env):
  """Custom Environment that follows gym interface"""
  metadata = {'render.modes': ['console']}

  def __init__(self, destination = [0,0,1], drone = olympe.Drone("10.202.0.1")):
    super(ParrotEnv, self).__init__()
    self.destination = destination
    self.drone = drone
    self.counter = 0
    self.q1 = LifoQueue()
    self.q2 = LifoQueue()
    self.agent_pos = [0,0,0]

    # Run the command for subscribing to the gazebo topic.
    ON_POSIX = 'posix' in sys.builtin_module_names
    command1 = "parrot-gz topic -e /gazebo/default/pose/info | grep  -A 5 'name: \"anafi4k\"'"
    command2 = "tlm-data-logger inet:127.0.0.1:9060"
    self.p = Popen(command1, stdout=PIPE, bufsize=1, close_fds=ON_POSIX, shell=True)
    self.v = Popen(command2, stdout=PIPE, bufsize=1, close_fds=ON_POSIX, shell=True)
    # Create a thread which dies with main program
    self.t1 = Thread(target = self.process_output1, args=(self.p.stdout, self.q1))
    self.t1.daemon = True
    self.t1.start()
    """
    self.t2 = Thread(target = self.process_output2, args=(self.v.stdout, self.q2))
    self.t2.daemon = True
    self.t2.start()
    """
    self.action_space = spaces.Box(low=np.array([-25,-25,-25]), high=np.array([25,25,25]),
                                        dtype=np.float32)
    self.observation_space = spaces.Box(low=np.array([-10,-10,-10]), high=np.array([10,10,10]),
                                        dtype=np.float32)


  # Process the output from the file
  def process_output1(self,out, queue):
    for line1 in iter(out.readline, b''):
      line1 = str(line1)
      if "x" in line1:
        number = re.findall(r"[-+]?\d*\.\d+|\d+", line1)[0]
        self.agent_pos[0] = float(number)
      if "y" in line1:
        number = re.findall(r"[-+]?\d*\.\d+|\d+", line1)[0]
        self.agent_pos[1] = float(number)
      if "z" in line1:
        number = re.findall(r"[-+]?\d*\.\d+|\d+", line1)[0]
        self.agent_pos[2] = float(number)
      queue.put(line1)
    out.close()
  """
  # Includes the drone velocities in state
  def process_output2(self,out, queue):
    for line2 in iter(out.readline, b''):
      line2 = str(line2)
      if ".worldLinearVelocity" in line2:
        number = re.findall(r"[-+]?\d*\.\d+|\d+", line2)[1]
        #print('--------------------------------',number)
        if ".x" in line2:
          self.agent_pos[2] = float(number)
        if ".y" in line2:
          self.agent_pos[3] = float(number)
        if ".z" in line2:
          self.agent_pos[5] = float(number)
      queue.put(line2)
    out.close()
  """

  def pos_feedback(self):
    for i in range(1):
      try:
        line1 = self.q1.get()
       # line2 = self.q2.get()
      except Empty:
        # Clear out the queue
        self.q1.queue.clear()
        #self.q2.queue.clear()

  def distance(self,a):
    # Calculates absolute distance from origin coordinate
    return math.sqrt(a[0]**2+a[1]**2+a[2]**2)

  def reset(self):
    # Resets the drone back to start of simulation after completion of episode
    self.pos_feedback() # Update state of the drone in self.agent_pos

    # Random initialization(reset) for every episode
    x_r = random.randrange(-5,5,1)
    y_r = random.randrange(-5,5,1)
    z_r = random.randrange(1,5,1)

    # Random goal setting for every episode
    x_d = random.randrange(-5,5,1)
    y_d = random.randrange(-5,5,1)
    z_d = random.randrange(1,5,1)

    self.destination = [x_d,y_d,z_d]

    print('------------RESET-------------',[x_r,y_r,z_r],'------------RESET-------------')
    print('------------GOAL-------------',self.destination,'------------GOAL-------------')

    # Move the drone to random initialization coordinate
    self.drone(moveBy(x_r-self.agent_pos[0], self.agent_pos[1]-y_r, self.agent_pos[2]-z_r, 0)>> FlyingStateChanged(state="hovering", _timeout=5)).wait()
    self.pos_feedback() # Update state of the drone in self.agent_pos
    obs = [self.agent_pos[0]-self.destination[0],self.agent_pos[1]-self.destination[1], self.agent_pos[2]-self.destination[2]]
    return np.array(obs).astype(np.float32)  # reward, done, info can't be included


  def step(self, action):
    # Takes action within set boundary limits with PCMD command, and updates state of the drone.
    self.pos_feedback()
    x=self.agent_pos[0]
    y=self.agent_pos[1]
    z=self.agent_pos[2]
    y_act = action[0]
    x_act = action[1]
    z_act = action[2]

    # Define bounded action
    if x>5.0:
      x_act = min(0,action[1])
    if y<-5.0:
      y_act = min(0,action[0])
    if x<-5:
      x_act = max(0,action[1])
    if y>5:
      y_act = max(0,action[0])
    if z<1:
      z_act = max(0,action[2])
    if z>5:
      z_act = min(0,action[2])

    self.drone(PCMD(1, y_act, x_act, 0, z_act, timestampAndSeqNum=0, _timeout=10)>> FlyingStateChanged(state="hovering", _timeout=5)).wait() 
    self.pos_feedback() # Update state of the drone in self.agent_pos
    obs = [self.agent_pos[0]-self.destination[0],self.agent_pos[1]-self.destination[1],self.agent_pos[2]-self.destination[2]]
    d = self.distance([obs[0],obs[1],obs[2]])

    #Terminating Condition and reward design
    done = bool(d < 0.5)
    if bool(d < 0.5):
      reward = +100   
    else:
      reward = -1*(d)
    print('------------STEPS-------------',self.counter,'------------STEPS-------------')
    print('------------REWARD----------',reward,'------------REWARD----------')

    info = {}

    self.counter += 1
    row = [self.counter,reward]
    with    open('reward.csv', 'a', newline='') as csvFile:
             writer = csv.writer(csvFile)
             writer.writerow(row)
             csvFile.close()
    print('------------STATE-------------',self.agent_pos,'------------STATE-------------')
    return np.array(obs).astype(np.float32), reward, done, info

  def render(self, mode='console'):
    print('------------STATE-------------',self.agent_pos,'------------STATE-------------')

  def close (self):
    pass


### Uncomment below lines to inspect check_env(env) after you modify the environment ###
'''
drone = olympe.Drone("10.202.0.1")
drone.connection()
assert drone(TakeOff()>> FlyingStateChanged(state="hovering", _timeout=5)).wait().success()
env = ParrotEnv(destination = [0,0,1], drone=drone)
print(env.observation_space)
print(env.action_space)
print('=============================================Check==================================================', check_env(env))
assert drone(Landing()).wait().success()
drone.disconnection()
'''
