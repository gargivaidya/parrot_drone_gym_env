"""
Benchmark reinforcement learning (RL) algorithms from Stable Baselines 2.10.
Author: Gargi Vaidya & Vishnu Saj
- Note : 

"""
import olympe
from parrotenv import ParrotEnv
from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, Landing,moveTo
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged, 
import os
import gym
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines import TD3
from stable_baselines.td3.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv

drone = olympe.Drone("10.202.0.1")
drone.connection()
assert drone(TakeOff()>> FlyingStateChanged(state="hovering", _timeout=5)).wait().success()

# Define the waypoints
A=[3,-3,3]
B=[3,3,5]
C=[-3,3,2]
D=[-3,-3,3]
obs=[0,0,0]

# Load the trained RL model
model = TD3.load("./tmp/best_model.zip")

# Evaluate model from origin state to waypoint A
env = ParrotEnv(destination = A, drone= drone)
done = 0
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
# Evaluate model from origin state to waypoint B
env = ParrotEnv(destination = B, drone= drone)
done = 0
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
# Evaluate model from origin state to waypoint C
env = ParrotEnv(destination = C, drone= drone)
done = 0
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
# Evaluate model from origin state to waypoint A
env = ParrotEnv(destination = D, drone= drone)
done = 0
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()

# Land the drone
assert drone(Landing()).wait().success()
drone.disconnection()
                       
