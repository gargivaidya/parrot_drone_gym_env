"""
Benchmark reinforcement learning (RL) algorithms from Stable Baselines 2.10.
Author: Gargi Vaidya & Vishnu Saj
- Note : Modify the RL algorithm from StableBaselines and tune the hyperparameters.

"""
import olympe
from matplotlib import pyplot as plt
from parrotenv import ParrotEnv
import subprocess
from olympe.messages.ardrone3.Piloting import TakeOff, moveBy, Landing,moveTo,PCMD
from olympe.messages.ardrone3.PilotingState import FlyingStateChanged, AttitudeChanged, moveByChanged, AltitudeChanged, PositionChanged
import os
import csv
import gym
import csv
import numpy as np
import matplotlib.pyplot as plt
from stable_baselines import TD3
from stable_baselines.td3.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import results_plotter
from stable_baselines.bench import Monitor
from stable_baselines.results_plotter import load_results, ts2xy
from stable_baselines.common.callbacks import BaseCallback

# Define the drone model and and take-off
drone = olympe.Drone("10.202.0.1")
drone.connection()
command = "echo '{\"jsonrpc\": \"2.0\", \"method\": \"SetParam\", \"params\": {\"machine\":\"anafi4k\", \"object\":\"lipobattery/lipobattery\", \"parameter\":\"discharge_speed_factor\", \"value\":\"0\"}, \"id\": 1}' | curl -d @- http://localhost:8383 | python -m json.tool"
subprocess.run(command, shell=True)
assert drone(TakeOff()>> FlyingStateChanged(state="hovering", _timeout=5)).wait().success()

class SaveOnBestTrainingRewardCallback(BaseCallback):
    """
    Callback for saving a model (the check is done every ``check_freq`` steps)
    based on the training reward (in practice, we recommend using ``EvalCallback``).
import csv
    :param check_freq: (int)
    :param log_dir: (str) Path to the folder where the model will be saved.
      It must contains the file created by the ``Monitor`` wrapper.
    :param verbose: (int)
    """
    def __init__(self, check_freq: int, log_dir: str, verbose=1):
        super(SaveOnBestTrainingRewardCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.log_dir = log_dir
        self.save_path = os.path.join(log_dir, 'best_model')
        self.best_mean_reward = -np.inf

    def _init_callback(self) -> None:
        # Create folder if needed
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self) -> bool:
        if self.n_calls % self.check_freq == 0:

          # Retrieve training reward
          x, y = ts2xy(load_results(self.log_dir), 'timesteps')
          if len(x) > 0:
              # Mean training reward over the last 100 episodes
              mean_reward = np.mean(y[-100:])
              if self.verbose > 0:
                print("Num timesteps: {}".format(self.num_timesteps))
                print("Best mean reward: {:.2f} - Last mean reward per episode: {:.2f}".format(self.best_mean_reward, mean_reward))

              # New best model, you could save the agent here
              if mean_reward > self.best_mean_reward:
                  self.best_mean_reward = mean_reward
                  # Example for saving best model
                  if self.verbose > 0:
                    print("Saving new best model to {}".format(self.save_path))
                  self.model.save(self.save_path)

        return True
# Stores a csv file for the episode reward       
heading = ["Timestep", "Reward"]
with    open('reward.csv', 'w', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(heading)
        csvFile.close()

# Create log directory
log_dir = "tmp1/"
os.makedirs(log_dir, exist_ok=True)

env = ParrotEnv(destination = [0,0,1], drone= drone)
#env.reset()
env = Monitor(env, log_dir)

model = TD3(MlpPolicy, env, verbose=1, learning_rate = 0.0005,tensorboard_log="./td3_parrot_tensorboard/", buffer_size = 25000)
callback = SaveOnBestTrainingRewardCallback(check_freq=1000, log_dir=log_dir)
model.learn(total_timesteps=30000, log_interval=10,tb_log_name = "td3_run_3d", callback = callback)
model.save("td3_parrot_3d")

# Land the drone and disconnect.
assert drone(Landing()).wait().success()
drone.disconnection()      
