import pywintypes
import OpenOPC
import requests
import time

pywintypes.datetime = pywintypes.TimeType  

# Connect to the OPC server
opc = OpenOPC.client()

# Connect to the PLC
opc.connect('OPC.SimaticHMI.CoRtHmiRTm.1')

#opc.connect('Matrikon.OPC.Simulation')
# Define the URL of the blockchain server
url = 'http://150.162.14.130:5000/data'

# Set up a continuous loop to read data from the PLC and send it to the blockchain server
while True:
    # Read the values of the PLC inputs and outputs
    inp = opc.read('Pick&Place.GV_B_Start_4','Pick&Place.GV_B_Reset_4','Pick&Place.GV_B_Stop_4',
                   'Pick&Place.GV_Sensor_Vacuo_4','Pick&Place.GV_Sensor_Prox_z_Recuado_4','Pick&Place.GV_Sensor_Prox_x_Recuado_4',
                   'Pick&Place.GV_Sensor_Prox_x_Avacado_4','Pick&Place.GV_Sensor_LUZ(1)_4','Pick&Place.GV_Sensor_LUZ(2)_4',
                   'Pick&Place.GV_Sensor_Optico_4','Pick&Place.GV_Sensor_Optico_Receptor_4')
    out = opc.read('Pick&Place.GV_LUZ_Start_4','Pick&Place.GV_LUZ_Reset_4','Pick&Place.GV_LUZ_Q1_4',
                   'Pick&Place.GV_LUZ_Q2_4','Pick&Place.GV_LUZ_Q5_4','Pick&Place.GV_LUZ_Q6_4',
                   'Pick&Place.GV_LUZ_Q4_4','Pick&Place.GV_Trava_4','Pick&Place.GV_Vacuo_4',
                   'Pick&Place.GV_Pistao_z_4','Pick&Place.GV_Pistao_x_Avanca_4','Pick&Place.GV_Pistao_x_Recua_4',
                   'Pick&Place.GV_Esteira_4','Pick&Place.GV_Transmissor_Optico_4')
    
    inputs = [int(input[0]) for input in inp]
    outputs = [int(output[0]) for output in out]
    # Combine the input and output values into a single list
    data = {'inputs': inputs, 'outputs': outputs}
    
    # Send the data to the blockchain server
    response = requests.post(url, json=data)
    
    # Wait for 1 second before repeating the process
    time.sleep(0.1)
    
# Disconnect from the PLC
opc.disconnect()
