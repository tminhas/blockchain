import requests
import time
import random
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# Define the URL of the blockchain server
url = 'http://192.168.1.9:5000/data'

# Load the server's public key for encryption
with open('public_key.pem', 'rb') as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )

# Load the client's private key for signature
with open('client_private_key.pem', 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

# Set up a continuous loop to read data from the PLC and send it to the blockchain server
while True:
    inputs = []
    outputs = []
    for i in range(4):
        inputs.append(random.randint(0, 1))
        outputs.append(random.randint(0, 1))
    # Combine the input and output values into a single list
    data = {'inputs': inputs, 'outputs': outputs}

    # Convert the data dictionary to a string
    data_str = str(data)

    # Encrypt the data using the server's public key
    encrypted_data = public_key.encrypt(
        data_str.encode('utf-8'),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # Sign the encrypted data using the client's private key
    signature = private_key.sign(
        encrypted_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    
    # Convert bytes to base64-encoded strings
    encrypted_data_str = base64.b64encode(encrypted_data).decode('utf-8')
    signature_str = base64.b64encode(signature).decode('utf-8')

    # Prepare the payload with the encrypted data and signature
    payload = {
        'data': encrypted_data_str,
        'signature': signature_str
    }

    # Send the payload to the blockchain server
    response = requests.post(url, json=payload)

    # Wait for 2 seconds before repeating the process
    time.sleep(2)
