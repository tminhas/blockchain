import time
import datetime
import json
from hashlib import sha256
from flask import Flask, render_template, request
from random import randint, random

my_ip = '127.0.0.1'

class Block:
    def __init__(self, index, bpm, timestamp, previous_hash, plc_data, validator):
        self.index = index
        self.bpm = bpm
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.plc_data = plc_data
        self.validator = validator

    def get_index(self):
        return self.index
    
    def get_bpm(self):
        return self.bpm
    
    def get_timestamp(self):
        return self.timestamp
    
    def get_previous_hash(self):
        return self.previous_hash

    def get_plc_data(self):
        return self.plc_data
    
    def get_validator(self):
        return self.validator
    
    def compute_hash(self):
        """ json dumps converts python object to a json string,
        using a dictionary to export the encoded data"""
        original_validator = self.validator
        self.validator = self.validator.to_list()[0]
        block_string = json.dumps(self.__dict__, sort_keys=True)
        self.validator = original_validator
        return sha256(block_string.encode()).hexdigest()
    
    def to_string(self):
        return 'Index: '+ str(self.get_index())+', BPM: '+ str(self.get_bpm()) + ", Previous Hash: " + str(self.get_previous_hash()) + ", Plc Data: " + str(self.get_plc_data())+", Validator: "+ str(self.get_validator().to_list()) +", Timestamp: " + str(self.get_timestamp())
    
    def to_list(self):
        return [self.index, self.bpm, self.timestamp, self.previous_hash, self.plc_data, int(self.validator.to_list()[0])]

class Validator:
    def __init__(self, id, tokens, age):
        self.creation_time = time.time()
        self.id = id
        self.tokens = tokens
        self.age = age
        
    def to_list(self):
        return [self.id, self.tokens, self.age]

class Blockchain:

    def __init__(self):
        self.chain = []
        self.start_genesis_block()
        self.index = 0
        self.validators = set()
        self.temporaryBlocks = []

    def start_genesis_block(self):
        """ initial blockchain block, with an index and a previous hash of 0"""
        genesis_block = Block(0, 1, str(datetime.datetime.now().replace(microsecond=0)), '0', '0'*32, Validator(1, 1, 1))
        self.chain.append(genesis_block) 
        return genesis_block
    
    def create_block(self, bpm, plc_data, validator):
        """
        Creates a temporary block to be validated
        """
        previous_hash = self.chain[-1].compute_hash()
        block = Block(self.index +1, bpm, str(datetime.datetime.now().replace(microsecond=0)), previous_hash , plc_data, validator)
        self.temporaryBlocks.append(block)
        return block
    
    def add_blocks(self, block):
        """
        Clears the temporary blocks and adds the block to the chain
        """
        self.temporaryBlocks = []
        self.index += 1
        return self.chain.append(block)
        
    def last_block(self):
        """
        Returns the last block in the chain
        """
        return self.chain[-1]
    

    def check_if_valid(self, chain):
        """
        Verifies if the previous hash from the blocks matches the block's hash 
        """
        previous_block = chain[0]
        current_block = 1
        
        while current_block < len(chain):
            block = chain[current_block]
            
            if block.get_previous_hash() != previous_block.compute_hash():
                return False
            
            previous_block = block
            current_block += 1
        
        return True
    def mass_removal(self):
        """
        If the chain is longer than 20, removes the first 10
        """
        if len(self.chain) >= 20:
            self.chain = self.chain[10:]
        return self.chain
    
    def add_validator(self, validator):
        """
        Creates a new validator for the blockchain
        """
        self.validators.add(validator)
        return self.validators
    
    def remove_validator(self, validator_id):
        """
        Removes a validator from the blockchain using the validators id
        """
        
        for validator in self.validators:
            if int(validator.to_list()[0]) == int(validator_id):
                self.validators.discard(validator) 
                return self.validators
                
        return self.validators
    
    def select_winner(self):
        """
        Creates a pool of validators,
        Adds the total amount of tokens among the validators,
        Selects a random number between 0 and the total amount of tokens
        Selects a winner
        """

        winnerPool = []
        totalTokens = 0
        
        for validator in self.validators:
            if validator.tokens > 0:
                winnerPool.append(validator)
                totalTokens += validator.tokens
        
        winnerNumber = randint(0, int(totalTokens))
        temp = 0
        
        for validator in winnerPool:
            temp += validator.tokens
            if winnerNumber < temp:
                return validator     
            
        return None
        
    def proof_of_stake(self):
        """
        Selects a validator as a winner, then adds the block to the blockchain
        giving the validator a portion of the bpm
        """   
        chosen_validator = self.select_winner()
        while chosen_validator == None:
            chosen_validator = self.select_winner()
        
        for block in self.temporaryBlocks:
            validator = block.get_validator()
            if validator.id == chosen_validator.id:
                chosen_block = block
                validator.tokens += chosen_block.bpm/50
                break

        self.add_blocks(chosen_block)
        return chosen_block
    
        
def plc_data_generator():
    data = ''
    for i in range(32):
        data += str(randint(0,1))
    return data    

val1 = Validator('1213', 1, 1)
val2 = Validator('1235', 1, 1)
val3 = Validator('1361', 1, 1)

blockchain = Blockchain()
blockchain.add_validator(val1)
blockchain.add_validator(val2)
blockchain.add_validator(val3)

app = Flask(__name__)

# Homepage
@app.route('/')
def home():
    return render_template('home.html')


# Displaying the blockchain
@app.route('/display_chain', methods=['GET'])
def display_chain():
    
    headings = ("Index", "BPM", "Timestamp", "Previous Hash", "PLC Data", "Validator")
    blocks = []
    
    for block in reversed(blockchain.chain):
        blocks.append(block.to_list())

    return render_template('display chain.html', blocks = blocks, headings = headings)


# Placing new validators in the blockchain
@app.route('/new_validator', methods=['GET', 'POST'])
def new_validator():
    if request.method == 'POST':
        id = request.form["id"]
        tokens = request.form["tokens"]
        
        new_validator = Validator(str(id), int(tokens), 1)
        blockchain.add_validator(new_validator)
        
        return render_template("new validator.html")
    return render_template("new validator.html")


# Displaying the current validators
@app.route('/current_validators', methods=['GET'])
def current_validators():
    headings = ("ID", "Tokens", "Age")
    validators = []
    for validator in blockchain.validators:
        time_now = time.time()
        validator.age = int(time_now - validator.creation_time)
        validators.append(validator.to_list())
        
    return render_template("current validators.html", headings=headings, validators=validators)


# Validating a new block
@app.route('/new_block', methods=['GET'])
def new_block():
    if blockchain.check_if_valid(blockchain.chain):
        headings = ("Index", "BPM", "Timestamp", "Previous Hash", "PLC Data", "Validator")
        block_bpm = randint(10,50)
        plc_data = plc_data_generator()
        
        for validator in blockchain.validators:
            time_now = time.time()
            validator.age = int(time_now - validator.creation_time)
            blockchain.create_block(block_bpm, plc_data, validator)
            
        winner_block = blockchain.proof_of_stake()
        bloco = winner_block.to_list()
        blockchain.mass_removal()
        
        return render_template('new block.html', winner_block=bloco, headings=headings)
    else:
        return render_template('failed validation.html')

@app.route('/remove_validator', methods=['GET', 'POST'])
def remove_validator():
    if request.method == 'POST':
        id = request.form['id']
        blockchain.remove_validator(id)
        
        return render_template('remove validator.html')
    return render_template('remove validator.html')


app.run(host=my_ip, port=5000)
