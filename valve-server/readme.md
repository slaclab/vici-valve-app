# VICI 12-Port Valve server 

## How to run: 

### Edit VICI_config.csv, enter device names and serial device path for the VICIs 

### Run the setup script:
chmod +x setup.sh 
bash setup.sh 

#### This script will: 

##### update valve-server.service and run.sh with the installed project path

##### setup python virtual environment (optional) 
python3 -m venv venv 
source venv/bin/activate

##### install dependencies 
pip install -r requirements.txt 



### web server will listen on 8972, could change this in server.py if desired.


### Start the server via the optional daemon setup: 
    systemctl enable valve-server.service 
    systemctl start valve-server.service

### ...or run in terminal session: 
    venv/bin/python server.py 
