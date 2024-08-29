# VICI 12-Port Valve GUIs 

utils/ defines some classes to display a 12-port valve, and represent it as a two-way or 3-way valve.  

stopflow.py is an example UI that builds off of those.

Global 'comms_enabled' can be used to switch off requests to the server, useful for developing a GUI.  (also probably a good idea to install jupyter to develop gui in notebook)

## How to run: 

### A. Run the setup script:

    chmod +x setup.sh 
    bash setup.sh 

#### This script will: 

1. update valve-frontend.service and run.sh with the installed project path

2. setup python virtual environment (optional) 
    >    python3 -m venv venv \
    >    source venv/bin/activate

3. install dependencies 
    > pip install -r requirements.txt 


### B. Run in a terminal session: 
    venv/bin/python stopflow.py 

#### or run as a daemon: 
    systemctl enable valve-server.service  
    systemctl start valve-server.service

(this will configure the service to start on boot so maybe not desirable right away.)
