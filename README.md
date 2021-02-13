# Gym Environment for Parrot Drone ANAFI 4K

OpenAI Gym compatible environment for the Parrot Drone ANAFI 4K for training reinforcement learning algorithms (compatible with Stable Baselines) integrated with the Parrot Sphinx simulation.

## Description

```parrotenv.py``` script contains the Gym.Env inherited class for the parrot drone. Modify the reward function as per goal task for drone. This script is designed for drone waypoint tracking with shortest distance. </br>
```parrot_training.py``` script trains the drone in Sphinx simulation for goal task using Stable Baseline algorithms and saves your best trained model. </br>
```parrot_predict.py``` script evaluates the saved model on the drone in Sphinx simulation. </br>




