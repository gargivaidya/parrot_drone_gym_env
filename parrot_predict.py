# # Script to load and run the trained TD3 model

import olympe
from parrotenv import ParrotEnv
from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, Landing,moveTo
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged, AttitudeChanged, moveByChanged, AltitudeChanged, PositionChanged

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
#drone.start_piloting()

A=[3,-3,3]
B=[3,3,5]
C=[-3,3,2]
D=[-3,-3,3]
obs=[0,0,0]
model = TD3.load("./tmp/best_model.zip")


env = ParrotEnv(destination = A, drone= drone)
done = 0
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
env = ParrotEnv(destination = B, drone= drone)
done = 0
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
env = ParrotEnv(destination = C, drone= drone)
done = 0
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()
env = ParrotEnv(destination = D, drone= drone)
done = 0
while not done:
    action, _states = model.predict(obs)
    obs, rewards, done, info = env.step(action)
    env.render()

#drone.start_piloting()
assert drone(Landing()).wait().success()
drone.disconnection()
                       
