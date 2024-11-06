"""Elements"""

# either

# self.add_element(Element(...))
# self.update_element("element_name", *args, **kwargs)

# or

# self.some_element = Element(...)
# self.add_element(element)
# self.some_element.update(*args, **kwargs)

"""Example Element"""
# old:
# doover_ui_variable(
#     "gaugePressure",
#     "Gauge Pressure (??)",
#     "float",
#     dec_precision=0,
#     ranges=[
#         {"label": "Low", "min": 0, "max": 5, "colour": "blue", "showOnGraph": True},
#         {"label": "Atmospheric", "min": 5, "max": 6, "colour": "green", "showOnGraph": True},
#         {"label": "High", "min": 5, "max": 10, "colour": "yellow", "showOnGraph": True},
#     ],
# ),

# new:
# ui.Variable(
#     "gaugePressure", "Gauge Pressure (??)", "float", dec_precision=0, ranges=[
#         Range("Low", min=0, max=5, colour=ui.Colour.blue),
#         Range("Atmospheric", min=5, max=6, colour=ui.Colour.green),
#         Range("High", min=6, max=10, colour=ui.Colour.yellow),
#     ]
# )

# or

# ui.NumericVariable(
#     "gaugePressure", "Gauge Pressure (??)", precision=0, ranges=[
#         Range("Low", min=0, max=5, colour=ui.Colour.blue),
#         Range("Atmospheric", min=5, max=6, colour=ui.Colour.green),
#         Range("High", min=6, max=10, colour=ui.Colour.yellow),
#     ]
# )

# other options could be BooleanVariable, TextVariable


"""Submodules"""

# either
class MyOtherSubmodule(...): ...

class MySubmodule(...):
    def __init__(self):
        self.add_element(...)
        self.add_element(...)
        self.add_submodule(MyOtherSubmodule())

# self.add_submodule(MySubmodule())

# or
# self.add_submodule(Submodule(Element(...), Element(...), Element(...))


"""COMMANDS"""
# note command callback only compatible with DDA/websockets
# either

class MyCommand(...):
    description = "..."
    def callback(self, *args, **kwargs):
        ...

# self.add_command(MyCommand())

# or

# @ui.command(description=...)
# def my_command(self, *args, **kwargs):
#     ...  # callback here



"""Critical Events"""

# either

# self.update_element("element_name", "value", critical=True)

# or define critical globally

# self.add_element(Element(..., critical=True))
# self.update_element("element_name", "value")


"""Log Manager"""

# self.set_log_interval(...)


"""Updating elements"""

# either

# self.update_element(...)
# self.push()  # alternatively, maybe self.sync() does a push and a pull? Should be in sync always, though...

# or

# self.update_element(..., immediate=True)  # maybe delayed=False?

# or

# with self.batch_update():
#      self.update_element(...)
#      self.update_element(...)
# implicit .push() is called


"""Coercing commands"""

# either

# self.my_command = MyCommand()
# self.add_command(my_command)
# somewhere else...
# self.my_command.coerce("some_value")

# or
# self.add_command(MyCommand())
# ...
# self.coerce_command("command_name", "some_value")

# or
# @ui.command(...)
# def my_command(...): ...
# ...
# self.my_command.coerce("some_value")


"""Significant Alerts / Crashes"""

# looks like this is just publishing to a channel. Can we just do

# self.api.publish_to_channel("significantAlerts", "some value")
# or
# self.dda_iface.publish_to_channel("significantAlerts", "some value")


ui1 = {'state': {'type': 'uiContainer', 'displayString': '', 'children': {'overviewPlot': {'type': 'uiMultiPlot', 'name': 'overviewPlot', 'displayString': 'Overview', 'series': ['lastTipTemp', 'lastTipHumidity', 'lastTipEmc'], 'colours': ['tomato', 'blue', 'limegreen'], 'activeSeries': [True, False, True]}, 'significantEvent': {'type': 'uiAlertStream', 'name': 'significantEvent', 'displayString': 'Notify me of any problems'}, 'selectedCrop': {'type': 'uiStateCommand', 'name': 'selectedCrop', 'displayString': 'Selected Crop', 'verboseString': 'Selected Crop', 'userOptions': {'spring_wheat': {'type': 'uiElement', 'name': 'spring_wheat', 'displayString': 'Spring Wheat'}, 'winter_wheat': {'type': 'uiElement', 'name': 'winter_wheat', 'displayString': 'Winter Wheat'}, 'durum_wheat': {'type': 'uiElement', 'name': 'durum_wheat', 'displayString': 'Durum Wheat'}, 'barley': {'type': 'uiElement', 'name': 'barley', 'displayString': 'Barley'}, 'peas': {'type': 'uiElement', 'name': 'peas', 'displayString': 'Peas'}, 'oats': {'type': 'uiElement', 'name': 'oats', 'displayString': 'Oats'}, 'canola': {'type': 'uiElement', 'name': 'canola', 'displayString': 'Canola'}, 'lentils': {'type': 'uiElement', 'name': 'lentils', 'displayString': 'Lentils'}, 'red_lentils': {'type': 'uiElement', 'name': 'red_lentils', 'displayString': 'Red Lentils'}, 'soybeans': {'type': 'uiElement', 'name': 'soybeans', 'displayString': 'Soybeans'}, 'flax': {'type': 'uiElement', 'name': 'flax', 'displayString': 'Flax'}, 'sunflower_seeds': {'type': 'uiElement', 'name': 'sunflower_seeds', 'displayString': 'Sunflower Seeds'}, 'long_grain_rice': {'type': 'uiElement', 'name': 'long_grain_rice', 'displayString': 'Long Grain Rice'}, 'corn': {'type': 'uiElement', 'name': 'corn', 'displayString': 'Corn'}, 'sorghum': {'type': 'uiElement', 'name': 'sorghum', 'displayString': 'Sorghum'}}, 'currentValue': 'oats'}, 'lastTipTemp': {'type': 'uiVariable', 'name': 'lastTipTemp', 'displayString': 'Tip Temperature (C)', 'form': 'radialGauge', 'varType': 'float', 'decPrecision': 1, 'ranges': [{'label': 'Low', 'min': 0, 'max': 20, 'colour': 'green', 'showOnGraph': False}, {'label': 'Warm', 'min': 20, 'max': 30, 'colour': 'yellow', 'showOnGraph': False}, {'label': 'High', 'min': 30, 'max': 40, 'colour': 'red', 'showOnGraph': False}], 'currentValue': -1}, 'lastTipHumidity': {'type': 'uiVariable', 'name': 'lastTipHumidity', 'displayString': 'Tip Humidity (%RH)', 'varType': 'float', 'decPrecision': 1, 'ranges': [{'label': 'Dry', 'min': 0, 'max': 30, 'colour': 'green', 'showOnGraph': False}, {'min': 30, 'max': 60, 'colour': 'blue', 'showOnGraph': False}, {'label': 'Humid', 'min': 60, 'max': 100, 'colour': 'yellow', 'showOnGraph': False}], 'currentValue': -1}, 'lastTipEmc': {'type': 'uiVariable', 'name': 'lastTipEmc', 'displayString': 'Tip Crop Moisture (%)', 'varType': 'float', 'decPrecision': 1, 'ranges': [{'min': 5, 'max': 8, 'colour': 'yellow', 'showOnGraph': False}, {'min': 8, 'max': 13, 'colour': 'blue', 'showOnGraph': False}, {'min': 13, 'max': 20, 'colour': 'yellow', 'showOnGraph': False}], 'currentValue': -1.0}, 'battVoltage': {'type': 'uiVariable', 'varType': 'float', 'name': 'battVoltage', 'displayString': 'Battery (V)', 'decPrecision': 1, 'ranges': [{'label': 'Low', 'min': 5.0, 'max': 6.0, 'colour': 'yellow', 'showOnGraph': True}, {'min': 6.0, 'max': 6.5, 'colour': 'blue', 'showOnGraph': True}, {'label': 'Good', 'min': 6.5, 'max': 7.5, 'colour': 'green', 'showOnGraph': True}, {'label': 'Over Voltage', 'min': 7.5, 'max': 8.0, 'colour': 'yellow', 'showOnGraph': True}], 'currentValue': 7.140415}, 'alarm_settings_submodule': {'type': 'uiSubmodule', 'name': 'alarm_settings_submodule', 'displayString': 'Alarms', 'children': {'emcAlarmSlider': {'type': 'uiSlider', 'name': 'emcAlarmSlider', 'displayString': 'Moisture Alarm (%)', 'min': 5, 'max': 30, 'stepSize': 0.1, 'dualSlider': True, 'icon': 'fa-regular fa-bell', 'showActivity': False, 'isInverted': False}, 'humidityAlarmSlider': {'type': 'uiSlider', 'name': 'humidityAlarmSlider', 'displayString': 'Relative Humidity Alarm (%)', 'min': 30, 'max': 95, 'stepSize': 0.1, 'dualSlider': True, 'showActivity': False, 'isInverted': False, 'icon': 'fa-regular fa-bell'}, 'tempAlarmSlider': {'type': 'uiSlider', 'name': 'tempAlarmSlider', 'displayString': 'Temperature Alarm (˚C)', 'min': -10, 'max': 50, 'stepSize': 0.1, 'showActivity': False, 'dualSlider': True, 'isInverted': False, 'icon': 'fa-regular fa-bell'}, 'batteryAlarm': {'type': 'uiSlider', 'name': 'batteryAlarm', 'displayString': 'Battery Alarm (V)', 'showActivity': False, 'min': 5, 'max': 10, 'stepSize': 0.1, 'dualSlider': False, 'isInverted': False}}}, 'details_submodule': {'type': 'uiSubmodule', 'name': 'details_submodule', 'displayString': 'Details', 'children': {'sleepTime': {'type': 'uiFloatParam', 'name': 'sleepTime', 'displayString': 'Periodic Sleep Time (mins)', 'min': 5, 'max': 1440}, 'pumpTime': {'type': 'uiFloatParam', 'name': 'pumpTime', 'displayString': 'Pump Time (secs)', 'min': 0, 'max': 300}, 'lastHeadTemp': {'type': 'uiVariable', 'name': 'lastHeadTemp', 'displayString': 'Head Temperature (C)', 'form': 'radialGauge', 'varType': 'float', 'decPrecision': 1, 'ranges': [{'label': 'Low', 'min': 0, 'max': 20, 'colour': 'green', 'showOnGraph': False}, {'label': 'Warm', 'min': 20, 'max': 30, 'colour': 'yellow', 'showOnGraph': False}, {'label': 'High', 'min': 30, 'max': 40, 'colour': 'red', 'showOnGraph': False}], 'currentValue': 16.07042}, 'lastHeadHumidity': {'type': 'uiVariable', 'name': 'lastHeadHumidity', 'displayString': 'Head Humidity (%RH)', 'varType': 'float', 'decPrecision': 1, 'ranges': [{'label': 'Dry', 'min': 0, 'max': 30, 'colour': 'green', 'showOnGraph': False}, {'min': 30, 'max': 60, 'colour': 'blue', 'showOnGraph': False}, {'label': 'Humid', 'min': 60, 'max': 100, 'colour': 'yellow', 'showOnGraph': False}], 'currentValue': 71.0428}}}, 'dashboard_submodule': {'type': 'uiSubmodule', 'name': 'dashboard_submodule', 'displayString': 'Dashboard Details', 'children': {'capacity': {'type': 'uiFloatParam', 'name': 'capacity', 'displayString': 'Maximum Storage Capacity (T)', 'min': 0, 'max': 10000, 'currentValue': 2000}, 'currentVolume': {'type': 'uiFloatParam', 'name': 'currentVolume', 'displayString': 'Current Volume (T)', 'min': 0, 'max': 10000, 'currentValue': 1800}}}, 'node_connection_info': {'type': 'uiConnectionInfo', 'name': 'node_connection_info', 'connectionType': 'periodic', 'connectionPeriod': 21600, 'nextConnection': 21600, 'allowedMisses': 4}}}}
ui2 = {'state': {'type': 'uiContainer', 'display_str': 'Device IO Tester', 'show_activity': True, 'children': {'disubmodule': {'name': 'disubmodule', 'type': 'uiSubmodule', 'display_str': 'Digital Inputs', 'show_activity': True, 'children': {'di-fetchnow': {'name': 'di-fetchnow', 'type': 'uiAction', 'display_str': 'Fetch Status Now', 'show_activity': True, 'colour': 'blue', 'requiresConfirm': True}, 'di-warning-1': {'name': 'di-warning-1', 'type': 'uiWarningIndicator', 'display_str': 'Digital Inputs are Scary!', 'show_activity': True, 'can_cancel': True}, 'di0-state': {'name': 'di0-state', 'type': 'uiVariable', 'display_str': 'DI0 State', 'show_activity': True, 'varType': 'bool', 'ranges': []}, 'di1-state': {'name': 'di1-state', 'type': 'uiVariable', 'display_str': 'DI1 State', 'show_activity': True, 'varType': 'bool', 'ranges': []}}}, 'dosubmodule': {'name': 'dosubmodule', 'type': 'uiSubmodule', 'display_str': 'Digital Outputs', 'show_activity': True, 'children': {'do0-toggle': {'name': 'do0-toggle', 'type': 'uiFloatParam', 'display_str': 'Digital Output 0 Toggle', 'show_activity': True}, 'do1-toggle': {'name': 'do1-toggle', 'type': 'uiFloatParam', 'display_str': 'Digital Output 1 Toggle', 'show_activity': True}, 'do0-state': {'name': 'do0-state', 'type': 'uiVariable', 'display_str': 'Digital Output {i} State', 'show_activity': True, 'varType': 'bool', 'ranges': []}, 'do1-state': {'name': 'do1-state', 'type': 'uiVariable', 'display_str': 'Digital Output {i} State', 'show_activity': True, 'varType': 'bool', 'ranges': []}, 'do2-state': {'name': 'do2-state', 'type': 'uiVariable', 'display_str': 'Digital Output {i} State', 'show_activity': True, 'varType': 'bool', 'ranges': []}, 'do3-state': {'name': 'do3-state', 'type': 'uiVariable', 'display_str': 'Digital Output {i} State', 'show_activity': True, 'varType': 'bool', 'ranges': []}, 'do4-state': {'name': 'do4-state', 'type': 'uiVariable', 'display_str': 'Digital Output {i} State', 'show_activity': True, 'varType': 'bool', 'ranges': []}, 'do2-toggle': {'name': 'do2-toggle', 'type': 'uiFloatParam', 'display_str': 'Digital Output 2 Toggle', 'show_activity': True}, 'do3-toggle': {'name': 'do3-toggle', 'type': 'uiFloatParam', 'display_str': 'Digital Output 3 Toggle', 'show_activity': True}, 'do4-toggle': {'name': 'do4-toggle', 'type': 'uiFloatParam', 'display_str': 'Digital Output 4 Toggle', 'show_activity': True}}}, 'ai-submodule': {'name': 'ai-submodule', 'type': 'uiSubmodule', 'display_str': 'Analog Inputs', 'show_activity': True, 'children': {'num-ai-var': {'name': 'num-ai-var', 'type': 'uiFloatParam', 'display_str': 'Number of Analog Inputs', 'show_activity': True}, 'ai-0-state': {'name': 'ai-0-state', 'type': 'uiVariable', 'display_str': 'Analog Input 0', 'show_activity': True, 'varType': 'float', 'ranges': []}, 'ai-1-state': {'name': 'ai-1-state', 'type': 'uiVariable', 'display_str': 'Analog Input 1', 'show_activity': True, 'varType': 'float', 'ranges': []}, 'ai-2-state': {'name': 'ai-2-state', 'type': 'uiVariable', 'display_str': 'Analog Input 2', 'show_activity': True, 'varType': 'float', 'ranges': []}, 'ai-3-state': {'name': 'ai-3-state', 'type': 'uiVariable', 'display_str': 'Analog Input 3', 'show_activity': True, 'varType': 'float', 'ranges': []}}}, 'sys-temp': {'name': 'sys-temp', 'type': 'uiVariable', 'display_str': 'System Temp', 'show_activity': True, 'varType': 'float', 'ranges': []}, 'sys-voltage': {'name': 'sys-voltage', 'type': 'uiVariable', 'display_str': 'System Voltage', 'show_activity': True, 'varType': 'float', 'ranges': []}, 'online': {'name': 'online', 'type': 'uiVariable', 'display_str': 'Online', 'show_activity': True, 'varType': 'time', 'currentValue': 1717025334.87972, 'ranges': []}}}}
