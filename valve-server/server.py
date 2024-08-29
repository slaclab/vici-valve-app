#!/home/pi/valve-server/venv/bin/python 

# Takes http requests to communicate with vici valves via valve_driver.py

from tornado import web, ioloop
# import json

from valve_driver import * 


def get_status(valve):
    if valve in VICI.valves: 
        return VICI.valves[valve].serial_is_open
    else: 
        print('valve name not found!') 
        return -1 


def get_status_all(): 
    if VICI.get_all_connections_open(): 
        return 'all_open'
    else: 
        return {v.name: v.serial_is_open for v in VICI.valves.values()}


def get_valve_position(valve): 
    if valve in VICI.valves: 
        return VICI.valves[valve].get_valve_position() 
    else: 
        print('valve name not found!') 
        return -1 


def set_valve_position(valve, position): 
    if valve in VICI.valves:
        success = VICI.valves[valve].set_valve_position(position) 
        if success: 
            return 1 
        else: 
            return 0 
    else: 
        print('valve name not found!') 
        return -1 


class ApiHandler(web.RequestHandler):
    '''API handler'''

    commands = ['get_status', 'get_status_all', 'get_valve_position', 'set_valve_position']

    def get(self, *args):
        print("api get, not supported")
        self.finish('')

    def post(self):
        print("got post")
        print("self.request.body: ", self.request.body)
        try:
            #data = json.loads(self.request.body)
            command = self.get_argument("id")
            print(f"api post w/: command: {command}")
        except: 
            print("invalid post") 
            return

        if command not in self.commands: 
            print("invalid command")
            self.finish({'success': 0, 'message': 'invalid command'})
            return

        try: 
            if command == 'get_status_all': 
                response = get_status_all()
            else: 
                try: 
                    valve = self.get_argument("valve")
                except: 
                    self.finish({'success': 0, 'message': 'missing valve argument'}); return

                if command == 'get_status': 
                    response = get_status(valve) 
                elif command == 'get_valve_position': 
                    response = get_valve_position(valve)
                elif command == 'set_valve_position': 
                    try: 
                        position = self.get_argument("position")
                    except: 
                        self.finish({'success': 0, 'message': 'missing position argument'}); return
                    response = set_valve_position(valve, position)
        except Exception as e: 
            print("failed to serve request") 
            self.finish({'success': 0, 'message': 'error'}); return 

        if response == -1: 
            self.finish({'success': 0, 'message': 'valve name not found'}); return 
        else: 
            self.finish({'success': 1, 'data': response}); return 


app = web.Application([
    (r'/api', ApiHandler),
])


if __name__ == '__main__':
    print("Establishing valve connections...") 
    setup_valves()

    port = 8972 
    print(f'Server is starting on port {port}')
    app.listen(port)
    ioloop.IOLoop.instance().start()


#####################################################################
# client side in valve-gui.py for reference
#####################################################################
# from requests import post

# def http_post(data, response_expected=False): 
#     if enable_comms == 0: 
#         return -1
#     try:
#         r = post(URL, data=data)
#         print("posted. r: ", r)
#         print(f'{r.text = }')
#         print(f'{r.status_code = }')
#     except Exception as e: 
#         print('post failed')
#         print(e)

#     if r.status_code != 200:
#         print("Status code: ", r.status_code)
#         if r.status_code == 503:
#             print("check that squid proxy is not connected, run 'kamo'")
#         return 0 
#     else: 
#         # success
#         if response_expected: 
#             return r.text 
#         else: 
#             return 1 


# def get_status(valve=None):
#     if valve is None: 
#         status = http_post({'id': 'get_status_all'}, response_expected=True)
#     else: 
#         status = http_post({'id': 'get_status', 'valve': valve}, response_expected=True)
#     return status 


# def post_valve_position(valve, position):
#     http_post({
#         'id': 'set_valve_position', 
#         'valve': valve,
#         'position': position
#     })


# def get_valve_position(valve): 
#     data = {
#         'id': 'get_valve_position', 
#         'valve': valve,
#     }
#     position = http_post(data, response_expected=True)
#     print("position returned: ", position)
#     return position

