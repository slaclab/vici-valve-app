# valve_driver controls VICI devices over serial.
#  Either configure the devices to use in VICI_config.csv, or just modify setup_valves() and enter them here directly. 

import os
import time
import serial

serial_id_1 = '/dev/serial/by-id/usb-FTDI_Chipi-X_FT5N6OYA-if00-port0'
serial_id_2 = '/dev/serial/by-id/usb-Belkin_USB_PDA_Adapter_0109_320165-if00-port0'
serial_id_3 = '/dev/serial/by-id/usb-FTDI_Chipi-X_FT5N6R5N-if00-port0'
serial_id_4 = '/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_D-if00-port0'


class VICI(): 
    '''Controls VICI valves over serial.  Instantiate with name and serial address.'''
    # if failing to connect, should try to reset the device id to None via the command *ID*
    # should try daisy chaining multiple devices and setting their id with ID[nn]
    valves = {}
    
    def __init__(self, name="v1", dev=serial_id_1, id_number=None): 
        self.name = name
        self.dev = dev 
        self.id_number = id_number 
        self.timeout = 3 # seconds for serial read timeout
        self.serial = None
        self.serial_is_open = False
        self.command_list_header = "Control Command List"
        self.serial_open_tries = 0 
        self.valve_position = None

        self.commands = {'command_list': '/?',     # get command list
                         'current_position': 'CP', # get current position
                         'go': 'GO',               # go to position 
                         'mode': 'AM',             # actuator mode, should return 3 for 'multiposition'
                         'response_mode': 'IFM'    # response mode, set to 0 for no response to action cmd
                        }
        
        VICI.valves[name] = self
        self.setup()
        
    def send(self, msg, check_if_open=True): 
        if self.serial_is_open or not check_if_open: 
            try: 
                if self.id_number is None: 
                    num_bytes_sent = self.serial.write(f'{msg}\r\n'.encode()) 
                else: 
                    num_bytes_sent = self.serial.write(f'{self.id_number}{msg}\r\n'.encode()) 
                return True
            except: 
                self.serial_is_open = False
        elif self.serial_open_tries < 5: 
            print("Serial connection is not open. Will try to open now.")
            self.open_serial_connection()
            self.send(msg)
        else: 
            print("Giving up. Take a closer look...device is turned off, serial cable unplugged, or usb-serial adapter replaced?")
            self.serial_open_tries = 0 
            return False

    def send_get(self, msg, check_if_open=True, wait_for_timeout=True, read_until=None): 
        if self.serial_is_open: 
            self.serial.flushInput()
        if self.send(msg, check_if_open): 
            if wait_for_timeout: 
                if read_until:
                    raw_reply = self.serial.read_until(read_until.encode())
                else:
                    raw_reply = self.serial.read_until(b'\r\n')
            else: 
                time.sleep(.1) # sleep a moment to allow time for response
                raw_reply = self.serial.read_all()
            reply = raw_reply.decode().strip()
            #print(f'Response: {reply}') 
            return reply 
        else: return False
    
    def setup(self): 
        self.open_serial_connection()
        if self.serial_is_open:
            self.check_actuator_mode()
            self.check_response_mode()

    def open_serial_connection(self): 
        print(f"------------\n{self.name} -- Opening usb-serial connection")
        print(f'serial device: {self.dev}')
        print(f'VICI ID: {self.id_number}')
        try:
            self.serial = serial.Serial(self.dev, timeout=self.timeout)
        except: 
            print("Attempt to open usb-serial connection failed -- USB unplugged?")
            self.serial_is_open = False 
            self.serial_open_tries += 1 
            return

        print('USB-serial opened. Sending test message to check serial...')
        raw_reply = self.send_get('/?', check_if_open=False, read_until="Displays This List\r\n") 
        if raw_reply.startswith(self.command_list_header): 
            self.serial_is_open = True 
            self.serial_open_tries = 0 
            print("Serial connection ready")
        else: 
            print("Did not get expected response! take a closer look: Serial cable unplugged, VICI is off, etc\n") 
            self.serial_is_open = False
            self.serial_open_tries += 1 

    def check_actuator_mode(self): 
        '''Check what mode the VICI is in, set to multiposition mode if not there already.'''
        try: 
            print("Checking VICI actuator mode")
            AM = self.send_get('AM')
            if AM == 'AM3': 
                print("Multiposition mode confirmed")
            else: 
                print(f"Changing AM from {AM} to 3")
                self.send(b'AM3')
        except Exception as e: 
            print("Failed to check actuator mode")
            print(e)
            
    def check_response_mode(self): 
        '''Tell VICI to not send a response for action commands.'''
        try: 
            print("Checking VICI response mode")
            IFM = self.send_get('IFM')
            if IFM == 'IFM0': 
                print("Response mode confirmed")
            else: 
                print(f"Changing IFM from {IFM} to 0")
                self.send(b'IFM0')
        except Exception as e: 
            print("Failed to check actuator mode")
            print(e)        
            
    def close(self): 
        self.serial.close() 

    def get_valve_position(self): 
        reply = self.send_get('CP')
        if reply.startswith('CP'):
            self.valve_position = int(reply.split('CP')[-1])
            print('current position: ', self.valve_position)
            return self.valve_position
        else: 
            return False
    
    def set_valve_position(self, valve_position): 
        if self.send(f'GO{valve_position}'):
            print(f'requested {valve_position}')
            #self.get_valve_position()  # dont confirm it got there, replies are too slow 
            self.valve_position = valve_position
            return True
        else: 
            return False

    def get_all_connections_open(): 
        return all([v.serial_is_open for v in VICI.valves.values()])
    
    def check_all_connections_open(): 
        if VICI.get_all_connections_open(): 
            print('All connections good!')
        else: 
            for v in VICI.valves.values(): 
                if not v.serial_is_open: 
                    print(f'{v.name} is not open') 


def import_valve_config(): 
    '''Will attempt to import a csv config file formatted as: 
            device_name_1, device_serial_addr_1
            device_name_2, device_serial_addr_2, 
            ...

        The parser is pretty raw...
    '''
    cfg_file = 'VICI_config.csv' 
    if cfg_file in os.listdir(): 
        try: 
            cfg_file_raw = open(cfg_file).read().strip()
            device_lines = cfg_file_raw.split('\n')
            devices_2d = []
            for line in device_lines: 
                if not line.startswith('#'):
                    if line.count(',') == 1: 
                        devices_2d.append(line.split(','))
            devices = {d[0]:d[1] for d in devices_2d}
            return devices
        except: 
            print("Failed to import config file")
            return 0 
    else: 
        # no config file found
        return 0 


def setup_valves(): 
    devices = import_valve_config()
    if not devices: 
        # no devices imported, using defaults
        v1 = VICI(name='v1', dev=serial_id_1)
        v2 = VICI(name='v2', dev=serial_id_2)
        v3 = VICI(name='v3', dev=serial_id_3)
        v4 = VICI(name='v4', dev=serial_id_4)
    else: 
        for name, serial_addr in devices.items(): 
            try: 
                VICI(name=name, dev=serial_addr)
            except: 
                print(f"Failed to setup {name}, {serial_addr}")
    print('\n\n\n----------------')
    VICI.check_all_connections_open()

