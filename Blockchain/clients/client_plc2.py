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
    inp = opc.read(['Testing.GV_B_Start_2', 'Testing.GV_B_Stop_2', 'Testing.GV_B_Reset_2',
                   'Testing.GV_Peca_Disponivel_2', 'Testing.GV_Peca_n_Preta_2', 'Testing.GV_Barreira_Luz_Seguranca_2',
                   'Testing.GV_Altura_Peca_Correta_2', 'Testing.GV_Cilindro_Levantado_2', 'Testing.GV_Cilindro_Abaixado_2', 
                   'Testing.GV_Cilindro_Ejeta_Retraido_2', 'Testing.GV_Estacao_Seguinte_Livre_2', 'Testing.GV_Manual_Mode_2'] 
                   )
    out = opc.read(['Testing.GV_LED_Reset_2', 'Testing.GV_LED_Start_2', 'Testing.PLC_2__Testing_Running_system',
                   'Testing.GV_Desce_Linear_2', 'Testing.GV_Sobe_Linear_2', 'Testing.GV_Ejeta_Peca_2', 'Testing.GV_AR_Rampa_2', 
                   'Testing.GV_IP_N_FO_2', 'Testing.GV_Running_System_2', 'Testing.GV_Running_Reset_2', 
                   'Testing.GV_LUZ_Q5_2', 'Testing.GV_LUZ_Q6_2'])
    
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
