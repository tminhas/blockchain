from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate a new RSA private key for the client
client_private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Serialize the client's private key to PEM format
client_private_key_pem = client_private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Save the client's private key to a file
with open('client_private_key.pem', 'wb') as key_file:
    key_file.write(client_private_key_pem)

# Extract the client's public key from the private key
client_public_key = client_private_key.public_key()

# Serialize the client's public key to PEM format
client_public_key_pem = client_public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Save the client's public key to a file
with open('client_public_key.pem', 'wb') as key_file:
    key_file.write(client_public_key_pem)
