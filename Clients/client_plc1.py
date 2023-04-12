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
    inp = opc.read('Distributing.GV_Magazine_Recuado_1', 'Distributing.GV_Magazine_Avancado_1', 'Distributing.GV_Vacuo_1',
                   'Distributing.GV_Peca_1', 'Distributing.GV_Sensor_Braco_Pega_P_1', 'Distributing.GV_Sensor_Braco_Solta_P_1',
                   'Distributing.GV_Estacao_Seguinte_Livre_1','Distributing.GV_B_Start_1','Distributing.GV_B_Stop_1',
                   'Distributing.GV_Manual_Mode_1', 'Distributing.GV_B_Reset_1')
    out = opc.read('Distributing.GV_Empurra_Peca_1', 'Distributing.GV_Liga_Vacuo_1', 'Distributing.GV_Liga_Sopro_1', 
                   'Distributing.GV_Rotativo_Pega_Peca_1', 'Distributing.GV_Rotativo_Solta_Peca_1', 'Distributing.PLC_1__Distributing_LED_Start'
                   'Distributing.PLC_1__Distributing_LED_reset', 'Distributing.GV_Running_Reset_1', 'Distributing.GV_Running_System_1')
    
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
