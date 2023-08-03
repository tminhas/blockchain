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
    inp = opc.read(['Fluid_Muscle_Press.GV_Detecta_peca_5','Fluid_Muscle_Press.GV_Esta_esquerda_5','Fluid_Muscle_Press.GV_Esta_direita_5',
                   'Fluid_Muscle_Press.GV_Esta_0_5','Fluid_Muscle_Press.GV_Esta_90_5','Fluid_Muscle_Press.GV_Esta_180_5',
                   'Fluid_Muscle_Press.GV_Esta_prensando_5','Fluid_Muscle_Press.GV_Saida_Autorizada_5','Fluid_Muscle_Press.GV_B_Start_5',
                   'Fluid_Muscle_Press.GV_B_Stop_5','Fluid_Muscle_Press.GV_B_Reset_5'])
    out = opc.read(['Fluid_Muscle_Press.GV_Garra_5','Fluid_Muscle_Press.GV_Mover_Esquerda_5','Fluid_Muscle_Press.GV_Mover_Direita_5',
                   'Fluid_Muscle_Press.GV_Braco_0_5','Fluid_Muscle_Press.GV_Braco_90_5','Fluid_Muscle_Press.GV_Braco_180_5',
                   'Fluid_Muscle_Press.GV_Prensa_5','Fluid_Muscle_Press.GV_Libera_Entrada_5','Fluid_Muscle_Press.GV_LUZ_Start_5',
                   'Fluid_Muscle_Press.GV_LUZ_Reset_5','Fluid_Muscle_Press.GV_LUZ_Q1_5','Fluid_Muscle_Press.GV_LUZ_Q2_5',
                   'Fluid_Muscle_Press.GV_LUZ_Q5_5','Fluid_Muscle_Press.GV_LUZ_Q6_5'])
    
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
