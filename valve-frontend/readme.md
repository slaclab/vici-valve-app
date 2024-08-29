# VICI 12-Port Valve GUIs 

utils/ defines some classes to display a 12-port valve, and represent it as a two-way or 3-way valve.  stopflow.py is an example UI that builds off of those.

## How to run: 

### Run the setup script:
chmod +x setup.sh 
bash setup.sh 

#### This script will: 

##### update valve-frontend.service and run.sh with the installed project path

##### setup python virtual environment (optional) 
python3 -m venv venv 
source venv/bin/activate

##### install dependencies 
pip install -r requirements.txt 


Then,

### Run in a terminal session: 
    venv/bin/python stopflow.py 

### or run as a daemon: 
    systemctl enable valve-server.service  # links to /etc/sytemd/system and will start on boot 
    systemctl start valve-server.service

global comms_enabled can be used to switch off requests to the server, useful for developing a GUI.
