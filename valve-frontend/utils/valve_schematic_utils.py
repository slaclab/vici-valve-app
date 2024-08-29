# Creates representational UI elements to build a schematic. 
# Can make simple on/off valves, 3-way valves, and add tubing/labels to link them together.
# Requires valve_12port_ui.  Maps through there to control the physical VICI valves.

from utils.valve_12port_ui import * 
import sys
from pathlib import Path
abspath = Path(__file__).parent

output_on = pn.pane.SVG(f'{abspath}/svg/line_on.svg') 
output_off = pn.pane.SVG(f'{abspath}/svg/line_off.svg') 
input_on = pn.pane.SVG(f'{abspath}/svg/line_on.svg') 
input_off = pn.pane.SVG(f'{abspath}/svg/line_off.svg') 
line_on = pn.pane.SVG(f'{abspath}/svg/line_on.svg')
line_off = pn.pane.SVG(f'{abspath}/svg/line_off.svg')
voutput_on = pn.pane.SVG(f'{abspath}/svg/vline_on.svg')
voutput_off = pn.pane.SVG(f'{abspath}/svg/vline_off.svg')
right_down_on = pn.pane.SVG(f'{abspath}/svg/line_on_right-down.svg') 
right_down_off = pn.pane.SVG(f'{abspath}/svg/line_off_right-down.svg') 
right_up_on = pn.pane.SVG(f'{abspath}/svg/line_on_right-up.svg') 
right_up_off = pn.pane.SVG(f'{abspath}/svg/line_off_right-up.svg') 
left_up_on = pn.pane.SVG(f'{abspath}/svg/line_on_left-up.svg') 
left_up_off = pn.pane.SVG(f'{abspath}/svg/line_off_left-up.svg') 
diag_fwd_on = pn.pane.SVG(f'{abspath}/svg/diag_fwd_on.svg') 
diag_fwd_off = pn.pane.SVG(f'{abspath}/svg/diag_fwd_off.svg') 
diag_back_on = pn.pane.SVG(f'{abspath}/svg/diag_back_on.svg') 
diag_back_off = pn.pane.SVG(f'{abspath}/svg/diag_back_off.svg') 


class Valve(param.Parameterized): 
    '''One port on a VICI 12 valve.  Drawn representationally in UI as a simple valve.
    Can link elements to the left and right of the valve, via
    left_tubing, right_tubing lists. They will highlight based on valve state.

    Create an instance by passing the parent 12-way valve ui object, and specify which port to 
    associate this valve with.  When this valve is switched off, specify which 'off_port' to set
    the 12-way valve to.
    '''

    name = param.String(default='valve')
    
    port = param.Integer(default=None, 
                            bounds=(1, 12), 
                            doc="Valve port on the VICI 12-way.", 
                           )
    off_port = param.Integer(default=None, 
                            bounds=(1, 12), 
                            doc="Port on the VICI 12-way when valve is off.", 
                           )

    state = param.Boolean(default=False)
    
    def __init__(self, 
                 v12_ui=None, 
                 left_tubing=['input'], 
                 right_tubing=['output', 'right_down'],
                 **params
                ):
        self.v12 = v12_ui
        self.left_tubing = left_tubing 
        self.right_tubing = right_tubing 

        super().__init__(**params)

        self.pane = None
        self.left_tubing_ui = pn.Row(*[getattr(sys.modules[__name__], n + '_off') for n in self.left_tubing])
        self.right_tubing_ui = pn.Row(*[getattr(sys.modules[__name__], n + '_off') for n in self.right_tubing]) 
        self.valve = pn.widgets.Button(icon=open(f'{abspath}/svg/valve.svg').read(), button_type='default', name='', icon_size='4em', width=75, height=75)
        self.valve.on_click(self.handle_valve)

        self.sync()

    def update_ui(self): 
        '''Redraw the UI after a valve state has changed.'''
        #print("updating ui")
        suffix = 'on' if self.state else 'off'
        if self.pane is None: 
            self.pane = pn.Row()
        else: 
            for i,n in enumerate([self.left_tubing_ui, self.valve, self.right_tubing_ui]):
                try: 
                    self.pane.remove(n)
                except Exception as E: 
                    print(f'couldnt remove {i}') 
                    print(E) 

        self.left_tubing_ui = pn.Row(*[getattr(sys.modules[__name__], f'{n}_{suffix}') for n in self.left_tubing])
        self.right_tubing_ui = pn.Row(*[getattr(sys.modules[__name__], f'{n}_{suffix}') for n in self.right_tubing])

        # add the newly updated ui elements to the pane 
        self.pane.insert(0, self.left_tubing_ui)
        self.pane.insert(1, self.valve) 
        self.pane.insert(2, self.right_tubing_ui)

    @param.depends('v12.valve_position', watch=True)
    def sync(self): 
        '''Sync the state of this representational valve with the current position of the physical parent 12-way valve.'''
        #print('syncing')
        self.state = self.v12.valve_position==self.port if self.v12 else False
        self.update_ui() 
        
    def handle_valve(self, event): 
        '''Called when valve button is clicked.  Will open/close the valve by interacting with the 
        parent 12-way valve object.'''
        # if self.state is None: 
        #     print(f'{self.name} state is None') 
        #     return 

        self.state = not self.state 
        if self.state: 
            self.open_valve() 
        else: 
            self.close_valve() 

        self.update_ui() 
        #print(f'{self.name} valve switched') 

    def open_valve(self): 
        #print("opening valve")
        self.v12.valve_position = self.port

    def close_valve(self): 
        #print("closing valve")
        self.v12.valve_position = self.off_port


class Valve3_diag(param.Parameterized): 
    '''3-way valve running off a VICI 12-port.  
    
    To create an instance, pass the parent 12-way valve ui object, and specify 
    which port to set it to when this 3-way valve is on or off. 

    There are some different ui elements and options for choosing the handedness of the 
    3-way valve to fit the layout of a schematic.  
    '''

    name = param.String(default='valve')
    
    port = param.Integer(default=None, 
                            bounds=(1, 12), 
                            doc="Valve port on the VICI 12-way.", 
                           )
    off_port = param.Integer(default=None, 
                            bounds=(1, 12), 
                            doc="Port on the VICI 12-way when valve is off.", 
                           )

    state = param.Boolean(default=False, allow_None=True)

    def __init__(self, 
                 v12_ui=None, 
                 righthanded=True,
                 upstream=None,
                 upstream_state=True,
                 mirror=None,
                 **params
                ):
        self.v12 = v12_ui
        self.righthanded = righthanded
        self.upstream = upstream
        self.upstream_state = upstream_state
        self.mirror = mirror
        self.input = input_off

        super().__init__(**params)

        self.valve = pn.widgets.Button(icon=open(f'{abspath}/svg/valve3.svg').read(), button_type='default', icon_size='4em', width=50, height=60)
        self.valve.on_click(self.handle_valve)
        self.pane = pn.Column()
        self.sync()

    def update_ui(self): 
        if self.state:
            if self.righthanded: 
                self.output1 = diag_fwd_off
                self.output2 = diag_back_on
            else: 
                self.output1 = diag_back_off
                self.output2 = diag_fwd_on
        elif self.state==False: 
            if self.righthanded: 
                self.output1 = diag_fwd_on
                self.output2 = diag_back_off
            else: 
                self.output1 = diag_back_on
                self.output2 = diag_fwd_off
        elif self.state is None: 
            if self.righthanded: 
                self.output1 = diag_fwd_off
                self.output2 = diag_back_off
            else: 
                self.output1 = diag_back_off
                self.output2 = diag_fwd_off

        self.pane.clear()
        if self.righthanded: 
            self.pane.extend([
                pn.Row(pn.Spacer(width=50), pn.Spacer(width=50), self.output1),
                pn.Row(self.input, self.valve, pn.Spacer(width=50)),
                pn.Row(pn.Spacer(width=50), pn.Spacer(width=50), self.output2)
            ])
        else: 
            self.pane.extend([
                pn.Row(self.output1, pn.Spacer(width=50), pn.Spacer(width=50)),
                pn.Row(pn.Spacer(width=50), self.valve, output_on),
                pn.Row(self.output2, pn.Spacer(width=50), pn.Spacer(width=50))
            ])

    @param.depends('upstream.state', watch=True)
    def update_input(self): 
        if self.upstream.state == self.upstream_state: 
            self.input = input_on
        else: 
            self.input = input_off
        self.update_ui()

    @param.depends('mirror.state', watch=True)
    def sync_mirror(self): 
        if self.mirror.state != self.state:
            self.handle_valve()
    
    @param.depends('v12.valve_position', watch=True)
    def sync(self): 
        self.sync_state()
        self.update_ui() 

    def sync_state(self): 
        if self.v12: 
            if self.v12.valve_position==self.port: 
                self.state = True
            elif self.v12.valve_position==self.off_port: 
                self.state = False
            else: 
                self.state = None
        else: 
            self.state = False
        
    def handle_valve(self, event=None): 
        self.sync_state()
        self.state = not self.state

        if self.state: 
            self.open_valve() 
        else: 
            self.close_valve() 

        self.update_ui() 
        #print(f'{self.name} valve switched') 

    def open_valve(self): 
        #print("opening valve")
        self.v12.valve_position = self.port

    def close_valve(self): 
        #print("closing valve")
        self.v12.valve_position = self.off_port


class Valve3_straight(Valve3_diag): 
    '''(basically the same as Valve3_diag but this class creates a UI with tubing inputs/outputs 
    at right angles instead of at 45 degrees) 
    
    3-way valve running off a VICI 12-port
    
    To create an instance, pass the parent 12-way valve ui object, and specify 
    which port to set it to when this 3-way valve is on or off. 

    There are some different ui elements and options for choosing the handedness of the 
    3-way valve to fit the layout of a schematic.  
    '''

    def __init__(self, orientation='rightdown', **params): 
        self.orientation = orientation 
        super().__init__(**params)

    def update_ui(self): 
        if self.upstream is None:
            self.input = input_on

        if self.orientation == 'rightdown': 
            if self.state:
                self.output1 = output_on
                self.output2 = voutput_off
            elif self.state==False: 
                self.output1 = output_off
                self.output2 = voutput_on
            else: 
                self.output1 = output_off
                self.output2 = voutput_off
        else: 
            print("not supported yet") 
        
        self.pane.clear()
        if self.righthanded: 
            self.pane.extend([
                pn.Row(pn.Spacer(width=50), pn.Spacer(width=50), pn.Spacer(width=50)),
                pn.Row(self.input, self.valve, self.output1),
                pn.Row(pn.Spacer(width=50), self.output2, pn.Spacer(width=50))
            ])
        else: 
            print("not supported yet")


class Tubing(param.Parameterized): 
    '''Tubing UI element. 
    
    Can use this to make schematic UIs and link valves together. The tubing can 
    link to a valve state by passing the valve in as 'upstream'.  This allows the 
    tubing to highlight based on the valve state.  
    
    Can chain multiple tubes together, and add a label in the middle. 
    '''

    state = param.Boolean(default=False)  
    
    def __init__(self, label=None, left_tubing=[], right_tubing=[], upstream=None, upstream_state=True, **params):
        self.label = label
        self.left_tubing = left_tubing
        self.right_tubing = right_tubing
        self.upstream = upstream
        self.upstream_state = upstream_state 
        
        super().__init__(**params)
        self.pane = pn.Row() 
        self.update_ui()
        
    @param.depends('upstream.state', watch=True)
    def update_ui(self, state=None):
        if self.upstream is not None: 
            self.state = self.upstream.state==self.upstream_state
        else: 
            self.state = self.state or False

        self.pane.clear()
        suffix = '_on' if self.state else '_off'
        self.left_tubing_active = [getattr(sys.modules[__name__], t + suffix) for t in self.left_tubing]
        self.right_tubing_active = [getattr(sys.modules[__name__], t + suffix) for t in self.right_tubing]

        if self.label: 
            self.pane.extend(self.left_tubing_active + [self.label] + self.right_tubing_active)
        else: 
            self.pane.extend(self.left_tubing_active + self.right_tubing_active)
