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
    inp = opc.read(['Sorting.GV_Sensor_OPE_6','Sorting.GV_Sensor_Indutivo_6','Sorting.GV_Sensor_OPC_6',
                   'Sorting.GV_Sensor_Retro_6','Sorting.GV_Sensor_Braco1_6','Sorting.GV_Sensor_Braco2_6',
                   'Sorting.GV_B_Start_6','Sorting.GV_B_Stop_6','Sorting.GV_B_Reset_6'])
    out = opc.read(['Sorting.GV_Esteira_6','Sorting.GV_Braco1_6','Sorting.GV_Braco1_6',
                   'Sorting.GV_Braco2_6','Sorting.GV_Pistao_6','Sorting.GV_Comunicacao_6',
                   'Sorting.GV_LUZ_Start_6','Sorting.GV_LUZ_Reset_6','Sorting.GV_LUZ_Q1_6',
                   'Sorting.GV_LUZ_Q2_6','Sorting.GV_LUZ_Q4_6','Sorting.GV_LUZ_Q5_6',
                   'Sorting.GV_LUZ_Q6_6','Sorting.GV_Prata_6','Sorting.GV_Vermelho_6',
                   'Sorting.GV_Preto_6'])
    
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
