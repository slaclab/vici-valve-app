# VICI 12-Port Valve server 

Web server will listen on 8972, could change this in server.py if you want.


## How to run: 

### A. Edit VICI_config.csv
Enter device names and serial device path for the VICIs 

### B. Run the setup script:
    chmod +x setup.sh 
    bash setup.sh 

#### This script will: 
1. update valve-server.service and run.sh with the installed project path

2. setup python virtual environment (optional) 
    >    python3 -m venv venv \
    >    source venv/bin/activate


3. install dependencies 
    > pip install -r requirements.txt 


### C. Start the server via the optional daemon setup: 
    systemctl enable valve-server.service 
    systemctl start valve-server.service

#### ...or run in terminal session: 
    venv/bin/python server.py 
