# Blockchain for Cyber-Physical Systems

This is an implementation of a blockchain using Python. 
It showcases the fundamental concepts of blockchain technology, including proof of work, proof of stake, and cryptographic hashing using SHA-256.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Clients](#clients)

## Features

- Database Integration: Implemented a relational database using Flask-SQLAlchemy to store and manage blockchain data efficiently.
- Data Persistence: Utilized database models and sessions to persist blockchain transactions, blocks, and validators' information between server restarts.
- Proof of Work (PoW): Validated the integrity of blocks using SHA-256 hashing and proof of work consensus algorithm stored in the database.
- Proof of Stake (PoS): Implemented a proof of stake algorithm using database data to select validators and create new blocks based on their economic stake in the network.
- Signature Verification: Employed cryptographic libraries to generate and verify time-based signatures to enhance data authenticity and security between the client and server.
- Flask Web Application: Includes a basic Flask web application to interact with the blockchain and demonstrate block mining and validation.

## Requirements

- Python 3.7 or higher
- Flask (for the web application)

## Installation

1. Clone this repository to your local machine.
2. Install the required Python packages using pip:

## Clients
The client scripts used in this project are for PLC communication using Python, for testing purposes there is a test client, which does not require a PLC connection.
