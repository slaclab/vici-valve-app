# http utilities to send requests to control 12-way valves to valve-server.
#
#  allows running the low level valve control on a lightweight device (eg raspberry pi), 
#   while running a heavier ui on a different machine.

from requests import post 

URL = 'http://localhost:8972/api'
#URL = 'http://192.168.0.102:8972/api'

# switch this off to test UI
comms_enabled = 0 

def http_post(data, response_expected=False): 
    if not comms_enabled: 
        return -1
    try:
        r = post(URL, data=data)
        #print("posted. r: ", r)
        #print(f'{r.text = }')
        #print(f'{r.status_code = }')
    except Exception as e: 
        print('post failed')
        print(e)

    if r.status_code != 200:
        print("Status code: ", r.status_code)
        if r.status_code == 503:
            print("check that proxy is not connected, run 'kamo'")  # BL15 specific
        return 0 
    else: 
        # success
        if response_expected: 
            return r.text 
        else: 
            return 1 

def get_status(valve=None):
    if valve is None: 
        status = http_post({'id': 'get_status_all'}, response_expected=True)
    else: 
        status = http_post({'id': 'get_status', 'valve': valve}, response_expected=True)
    return status 


def post_valve_position(valve, position):
    http_post({
        'id': 'set_valve_position', 
        'valve': valve,
        'position': position
    })


def get_valve_position(valve): 
    data = {
        'id': 'get_valve_position', 
        'valve': valve,
    }
    position = http_post(data, response_expected=True)
    print("position returned: ", position)
    return position
