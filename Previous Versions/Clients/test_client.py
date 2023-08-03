import requests
import time
import random

# Define the URL of the blockchain server
url = 'http://192.168.1.5:5000/data'

# Set up a continuous loop to read data from the PLC and send it to the blockchain server
while True:
    inputs = []
    outputs = []
    for i in range(4):
        inputs.append(random.randint(0, 1))
        outputs.append(random.randint(0, 1))
    # Combine the input and output values into a single list
    data = {'inputs': inputs, 'outputs': outputs}
    
    # Send the data to the blockchain server
    response = requests.post(url, json=data)
    
    # Wait for 1 second before repeating the process
    time.sleep(2)
    