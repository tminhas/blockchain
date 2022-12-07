import time
import datetime
import json
from hashlib import sha256
from flask import Flask, render_template
import struct
#https://docs.python.org/3/library/struct.html


class Block:
    def __init__(self, index, nounce, timestamp, previous_hash, plc_data):
        self.index = index
        self.nounce = nounce
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.plc_data = plc_data

    def get_index(self):
        return self.index
    
    def get_nounce(self):
        return self.nounce
    
    def get_timestamp(self):
        return self.timestamp
    
    def get_previous_hash(self):
        return self.previous_hash

    def get_plc_data(self):
        return self.plc_data
    
    def compute_hash(self):
        """ json dumps converts python object to a json string,
        using a dictionary to export the encoded data"""
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()
    
    def to_string(self):
        return 'Index: '+ str(self.get_index())+', Nounce: '+ str(self.get_nounce()) + ", Previous Hash: " + str(self.get_previous_hash()) + ", Plc Data: " + str(self.get_plc_data())+ ", Timestamp: " + str(self.get_timestamp())
    

class Blockchain:

    def __init__(self):
        self.chain = []
        self.start_genesis_block()
        self.index = 0

    def start_genesis_block(self):
        """ initial blockchain block, with an index and a previous hash of 0"""
        genesis_block = Block(0, 1, str(datetime.datetime.now()), '0', 'idk yet')
        self.chain.append(genesis_block)

        return genesis_block

    def create_block(self, nounce, previous_hash, plc_data):
        self.index += 1
        block = Block(self.index, nounce, str(datetime.datetime.now()), previous_hash, plc_data)
        self.chain.append(block)
        return block

    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_nounce):
        new_nounce = 1
        check_nounce = False

        while check_nounce is False:
            hash_operation = sha256(
                str(new_nounce**2 - previous_nounce**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_nounce = True
            else:
                new_nounce += 1

        return new_nounce

    def check_if_valid(self, chain):
            previous_block = self.chain[0]
            current_block = 1
            
            while current_block < len(self.chain):
                block = chain[current_block]
                if block.get_previous_hash() != previous_block.compute_hash():
                    return False
                
                previous_nounce = previous_block.get_nounce()
                nounce = block.get_nounce()
                hash_operation = sha256(str(nounce**2 - previous_nounce**2).encode()).hexdigest()
                
                if hash_operation[:5] != '00000':
                    return False
                previous_block = block
                current_block += 1
            
            return True
 
    def mass_removal(self):
        if len(self.chain) >= 20:
            self.chain = self.chain[10:]
        return self.chain

# Creating Web App
app = Flask(__name__)

blockchain = Blockchain()

# Homepage
@app.route('/')
def home():
    return render_template('home.html')

# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
    blockchain.mass_removal()
    
    start_time = time.time()
    if blockchain.check_if_valid(blockchain.chain):
        
        
        previous_block = blockchain.last_block()
        previous_nounce = previous_block.get_nounce()
        nounce = blockchain.proof_of_work(previous_nounce)
        previous_hash = previous_block.compute_hash()
        
        plc_data = '0101010101010101'
        
        block = blockchain.create_block(nounce, previous_hash, plc_data)
        minerado = block.to_string()

        end_time = time.time()
        return render_template('mining.html', blk = minerado, time = end_time - start_time)
    else:
        return render_template('failed mining.html')


# Displaying the blockchain
@app.route('/display_chain', methods=['GET'])
def display_chain():
    
    blocks = []
    
    for block in blockchain.chain:
        blocks.append(block.to_string())
        
    return render_template('display chain.html', chain = blocks)

app.run(host='127.0.0.1', port=5000)