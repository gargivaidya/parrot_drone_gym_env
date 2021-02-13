# Gym Environment for Parrot Drone ANAFI 4K

OpenAI Gym compatible environment for the Parrot Drone ANAFI 4K for training reinforcement learning algorithms (compatible with Stable Baselines) integrated with the Parrot Sphinx simulation.


## Description

```parrotenv.py``` script contains the Gym.Env inherited class for the parrot drone. Modify the reward function as per goal task for drone. This script is designed for drone waypoint tracking with shortest distance. </br>
```parrot_training.py``` script trains the drone in Sphinx simulation for goal task using Stable Baseline algorithms and saves your best trained model. Tune the hyperparameters for best reward performance per episode. </br>
```parrot_predict.py``` script evaluates the saved model on the drone in Sphinx simulation. </br>

## Installation Setup
This script needs Parrot-Sphinx and Olympe on Ubuntu 18.04. No ROS installation required.
### Parrot-Sphinx
Parrot-Sphinx Documentation - https://developer.parrot.com/docs/sphinx/whatissphinx.html
``` 
echo "deb http://plf.parrot.com/sphinx/binary `lsb_release -cs`/" | sudo tee /etc/apt/sources.list.d/sphinx.list > /dev/null 
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 508B1AE5

sudo apt update 
sudo apt install parrot-sphinx

sudo systemctl start firmwared.service
```

### Olympe
Olympe Documentation - https://developer.parrot.com/docs/olympe/overview.html

```
cd $HOME
mkdir -p code/parrot-groundsdk
cd code/parrot-groundsdk
pwd
repo init -u https://github.com/Parrot-Developers/groundsdk-manifest.git
repo sync

cd code/parrot-groundsdk
pwd
./products/olympe/linux/env/postinst

```
## Training
Luanch simulation and spawn the drone model in the desired world. Run the training script. </br>
`sphinx <path/to/my.world> <path/to/my.drone>` </br>

`sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/virt_anafi4k.drone ` </br>
In a separate terminal - </br>
`source ~/code/parrot-groundsdk/./products/olympe/linux/env/shell
python parrot_training.env`

## Evaluation
Launch the simulation Spawn the drone model in the desired world. Run the evaluation script. </br>
`sphinx <path/to/my.world> <path/to/my.drone>` </br>

`sphinx /opt/parrot-sphinx/usr/share/sphinx/drones/virt_anafi4k.drone ` </br>
In a separate terminal - </br>
`source ~/code/parrot-groundsdk/./products/olympe/linux/env/shell
python parrot_predict.env`

## Disable drone battery in simulation

In a new bash terminal - </br>
`echo '{"jsonrpc": "2.0", "method": "SetParam", "params": {"machine":"anafi4k", "object":"lipobattery/lipobattery", "parameter":"discharge_speed_factor", "value":"0"}, "id": 1}' | curl -d @- http://localhost:8383 | python -m json.tool`





