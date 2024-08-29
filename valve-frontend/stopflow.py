#!/usr/bin/env python

# A schematic web-based UI for stopflow 
# Using valve_schematic_utils to draw valves and tubing, which 
# communicate with VICI 12-way valves over http. 

# UI has 3 sections, different ways of viewing/manipulating the circuit: 
#  - directly display the 12-port valve and the current position
#  - high level mode buttons
#  - schematic with representational valves

# set comms_enabled = 0 to turn off comms with server/vici


from utils.valve_schematic_utils import * 

########################################################
# Valves

# Stopflow uses 4 VICI units, each in a '3-way valve' setup
########################################################

v12_FeCN6 = Valve12_UI(name='fecn6')
v12_water = Valve12_UI(name='water')
v12_hellmanex = Valve12_UI(name='syringe_inlet')
v12_HCl = Valve12_UI(name='syringe_outlet')

# Set up the representational 3-way valve elements, and the tubing objects that connect them.
v_FeCN6 = Valve3_straight(v12_ui=v12_FeCN6, name='Fe(CN)6', port=2, off_port=1) #right_tubing=['output', 'line', 'right_down']
FeCN6_tubing = Tubing(label='## --> To Sample', left_tubing=['line'], upstream=v_FeCN6)

v_water = Valve3_straight(v12_ui=v12_water, name='water', port=2, off_port=1) #right_tubing=['output', 'line', 'right_down']
water_tubing = Tubing(label='## --> To Sample', left_tubing=['line'], upstream=v_water)

v_hellmanex = Valve3_straight(v12_ui=v12_hellmanex, name='hellmanex', port=2, off_port=1) #right_tubing=['output', 'line', 'right_down']
hellmanex_tubing = Tubing(label='## --> To Sample', left_tubing=['line'], upstream=v_hellmanex)

v_HCl = Valve3_straight(v12_ui=v12_HCl, name='HCl', port=2, off_port=1) #right_tubing=['output', 'line', 'right_down']
HCl_tubing = Tubing(label='## --> To Sample', left_tubing=['line'], upstream=v_HCl)


########################################################
# Mode Buttons 

# Create high level buttons that switch operational mode.  

# example event object: 
# Event(what='value', name='clicks', obj=Button(button_type='primary', clicks=3, height=60, name='Water Mode', sizing_mode='fixed', width=120), 
#  cls=Button(button_type='primary', clicks=3, height=60, name='Water Mode', sizing_mode='fixed', width=120), old=2, new=3, type='set')
########################################################

selected_mode = None

def update_selected_mode(btn): 
    # change active button color to green
    global selected_mode
    if selected_mode: 
        selected_mode.button_type = 'primary'
    selected_mode = btn
    selected_mode.button_type = 'success'


def FeCN6_mode(event): 
    v_water.close_valve()
    v_hellmanex.close_valve()
    v_HCl.close_valve()

    v_FeCN6.open_valve()
    update_selected_mode(event.obj)

def water_mode(event): 
    v_FeCN6.close_valve()
    v_hellmanex.close_valve()
    v_HCl.close_valve()

    v_water.open_valve()
    update_selected_mode(event.obj)

def hellmanex_mode(event): 
    v_FeCN6.close_valve()
    v_water.close_valve()
    v_HCl.close_valve()

    v_hellmanex.open_valve()
    update_selected_mode(event.obj)    

def HCl_mode(event): 
    v_FeCN6.close_valve()
    v_water.close_valve()
    v_hellmanex.close_valve()

    v_HCl.open_valve()
    update_selected_mode(event.obj)
    
FeCN6_button = pn.widgets.Button(name='Fe(CN)6 Mode', button_type='primary', width=120, height=60)
FeCN6_button.on_click(FeCN6_mode)

water_button = pn.widgets.Button(name='Water Mode', button_type='primary', width=120, height=60)
water_button.on_click(water_mode)

hellmanex_button = pn.widgets.Button(name='Hellmanex Mode', button_type='primary', width=120, height=60)
hellmanex_button.on_click(hellmanex_mode)

HCl_button = pn.widgets.Button(name='HCl Mode', button_type='primary', width=120, height=60)
HCl_button.on_click(HCl_mode)


########################################################
# UI 
########################################################

def hspace(): 
    return pn.Spacer(sizing_mode='stretch_width')

def bluebar(): 
    return pn.Row(pn.Spacer(sizing_mode='stretch_width', styles=dict(background='lightgrey'), height=5))

def whitebar(): 
    return pn.Row(pn.Spacer(sizing_mode='stretch_width', styles=dict(background='white'), height=5))

spacer = pn.Spacer(width=30)

stopflow_gui = pn.Column(
    pn.Row(hspace(), '# BL9-3 Stop Flow', hspace()), 
    pn.Row(hspace(), FeCN6_button, water_button, hellmanex_button, HCl_button, hspace()),
    #bluebar(),

    ###############################################
    # V12 Section
    
    pn.Row(hspace(),
           pn.Column(pn.Row(hspace(), '## Fe(CN)6 Valve', pn.Spacer(sizing_mode='stretch_width')), v12_FeCN6.pane), 
           spacer, 
           pn.Column(pn.Row(hspace(), '## Water Valve', hspace()), v12_water.pane), 
           spacer, 
           pn.Column(pn.Row(hspace(), '## Hellmanex Valve', hspace()), v12_hellmanex.pane),
           spacer, 
           pn.Column(pn.Row(hspace(), '## HCl Valve', hspace()), v12_HCl.pane), 
           hspace() 
          ),
    # bluebar(),

    # ###############################################
    # # Schematic

    # pn.Row(hspace(), '## Schematic', hspace()),
    # pn.Row('## Fe(CN)6', v_FeCN6.pane, FeCN6_tubing.pane),
    # pn.Spacer(height=60),

    # pn.Row('## Water', v_water.pane, water_tubing.pane),
    # pn.Spacer(height=60),

    # pn.Row('## Hellmanex', v_hellmanex.pane, hellmanex_tubing.pane),
    # pn.Spacer(height=60),

    # pn.Row('## HCl', v_HCl.pane, HCl_tubing.pane),
    # pn.Spacer(height=60),

    # bluebar(), 
    #whitebar()
)


if __name__ == "__main__":
    comms_enabled = 0 
    #x = stopflow_gui.show(title="Valves", address="192.168.0.10", port=9891, websocket_origin="192.168.0.10:9891", interactive=True)
    x = stopflow_gui.show(title="Valves", address="localhost", port=9891, websocket_origin="localhost:9891", interactive=True)
