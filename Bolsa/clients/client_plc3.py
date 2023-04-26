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
    
    #input era pra ter 10 tags mas só tem 8
    inp = opc.read('Separating.GV_S_Chegada_3','Separating.GV_S_Presenca_3','Separating.GV_S_Altura_3',
                   'Separating.GV_S_Descarte_3','Separating.GV_S_Final_3','Separating.GV_B_Start_3',
                   'Separating.GV_B_Stop_3','Separating.GV_B_Reset_3')
    out = opc.read('Separating.GV_Motor_P_3', 'Separating.GV_Motor_D_3', 'Separating.GV_Pino_3',
                    'Separating.GV_Garra_3', 'Separating.GV_IP_N_FO_3', 'Separating.GV_LUZ_Start_3',
                    'Separating.GV_LUZ_Reset_3', 'Separating.GV_LUZ_Q1_3','Separating.GV_LUZ_Q2_3')
    
    inputs = [int(inpu[0]) for inpu in inp]
    outputs = [int(output[0]) for output in out]
    # Combine the input and output values into a single list
    data = {'inputs': inputs, 'outputs': outputs}
    
    # Send the data to the blockchain server
    response = requests.post(url, json=data)
    
    # Wait for 1 second before repeating the process
    time.sleep(0.1)
    
# Disconnect from the PLC
opc.disconnect()
