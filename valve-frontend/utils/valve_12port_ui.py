# Web-based UI element for a VICI 12-port valve
#  communicates over http with valve-server

from utils.valve_frontend_http_utils import * 

import panel as pn
import param


class Valve12_UI(param.Parameterized): 
    valve_position = param.Integer(default=None, 
                                    bounds=(1, 12), 
                                    doc="Valve position selected", 
                                    allow_None=True, 
                                    allow_refs=True
                                   )
    name = param.String(default='A')

    valves = []
    connection_status = param.Boolean(default=False) 

    def __init__(self, **params):
        #self.v12 = valve_12_way  # if running the valve_driver on the same machine can reference it here to bypass the http layer
        super().__init__(**params)
        self.pane = None
        self.valves.append(self) 

        self.buttons = {i: pn.widgets.Button(name=str(i), button_type='default', icon_size='4em', width=30, height=30) for i in range(1,13)}
        for b in self.buttons.values():
            b.on_click(self.set_valve_position)

        self.draw_ui()
        self.get_valve_position()
        

    def draw_ui(self): 
        twelve = pn.Row(
            pn.Spacer(width=95, height=30), 
            self.buttons[12], 
            pn.Spacer(width=90, height=30)
        )
        one = pn.Row(
            pn.Spacer(width=50, height=30), 
            self.buttons[11],
            pn.Spacer(width=40, height=30),
            self.buttons[1],
            pn.Spacer(width=55, height=30)
        )
        two = pn.Row(
            pn.Spacer(width=25, height=30), 
            self.buttons[10],
            pn.Spacer(width=90, height=30),
            self.buttons[2],
            pn.Spacer(width=30, height=30), 
        )
        three = pn.Row(
            self.buttons[9],
            pn.Spacer(width=140, height=30),
            self.buttons[3]
        )
        four = pn.Row(
            pn.Spacer(width=25, height=30), 
            self.buttons[8],
            pn.Spacer(width=90, height=30),
            self.buttons[4],
            pn.Spacer(width=30, height=30), 
        )
        five = pn.Row(
            pn.Spacer(width=50, height=30), 
            self.buttons[7],
            pn.Spacer(width=40, height=30),
            self.buttons[5],
            pn.Spacer(width=55, height=30)
        )
        six = pn.Row(
            pn.Spacer(width=95, height=30), 
            self.buttons[6],
            pn.Spacer(width=90, height=30)
        )
        self.pane = pn.Column(twelve, one, two, three, four, five, six)

    @param.depends('valve_position', watch=True)
    def set_valve_position(self, event=None): 
        '''This method can get called either by clicking one of the 12-way valves UI buttons (via button on_click), 
        or by a representational valve that points to this one (via param). 

        Either way, this method will route the change to physically move the VICI, and then will keep the 12-way UI 
        up to date by highlighting the current position.
        '''
        #print(f'valve {self.name} switched') 

        if event is not None: 
            # function was called by a button click event
            if self.valve_position != (port_number := int(event.obj.name)): 
                self.valve_position = port_number
                # now can return, func will be called again from param.depends
                return

        # function was called by param.depends
        #print('param.depends - self.valve_position: ', self.valve_position)
        self.move_valve()

        # update selected button highlight
        for b in self.buttons.values(): 
            if int(b.name) == self.valve_position: 
                b.button_type = 'success'
            else: 
                b.button_type = 'default'
                
    def move_valve(self): 
        #print(f'moving valve to {self.valve_position}') 
        #self.v12.set_valve_position(self.valve_position)
        if not comms_enabled: 
            return
        post_valve_position(self.name, self.valve_position)

    def get_valve_position(self): 
        if not comms_enabled: 
            return
        position = get_valve_position(self.name)
        if position == -1: 
            print(f'failed to get valve position for {self.name}')
        elif position == self.valve_position: 
            pass 
        else: 
            self.valve_position = position

    def get_status(self): 
        if not comms_enabled: 
            return
        self.connection_status = get_status(self.name)

