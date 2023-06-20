import time
import datetime
import json
from threading import Thread
from hashlib import sha256
from flask import Flask, render_template, request
from random import randint, random
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker


my_ip = "192.168.1.5"
# tempo para criação de um bloco caso não tenham mudanças
background_timer1 = 30
global plc_data
plc_data = dict()
zeros_in_hash = 5

# configs para banco de dados
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def create_session():
    with app.app_context():
        Session = sessionmaker(bind=db.engine)
        session = Session()
        return session

session = create_session()
class Box:
    def __init__(self, blks, previous_hash, nounce, timestamp):
        self.blks = blks
        self.previous_hash = previous_hash
        self.nounce = nounce
        self.timestamp = timestamp
        
    def get_previous_hash(self):
        return self.previous_hash

    def get_nounce(self):
        return self.nounce
    
    def compute_hash(self):
        """ json dumps converts python object to a json string,
        using a dictionary to export the encoded data"""
        self_str = self.to_string()
        return sha256(self_str.encode()).hexdigest()
    
    def to_list(self):
        print(self.blks)
        return [self.blks[0].get_index(), self.blks[-1].get_index(), self.previous_hash, self.nounce, self.timestamp]
    
    def to_string(self):
        self_str = ""
        for blocks in self.blks:
            self_str += blocks.to_string()
        self_str += str(self.previous_hash) +" "+str(self.nounce)
        return self_str 

class Block(db.Model):
    __tablename__ = 'blocks'
    id = db.Column(db.Integer, primary_key=True)
    indx = db.Column(db.Integer)
    bpm = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    previous_hash = db.Column(db.String(64))
    plc_data = db.Column(db.String(255))

    def __init__(self, indx, bpm, timestamp, previous_hash, plc_data, validator):
        self.indx = indx
        self.bpm = bpm
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.plc_data = plc_data
        self.validator = validator

    def get_index(self):
        return self.indx
    
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
        block_string = self.to_string()
        return sha256(block_string.encode()).hexdigest()
    
    def to_string(self):
        validator_dict = self.validator.to_dict()
        block_dict = {
            'index': self.indx,
            'timestamp': str(self.timestamp),
            'bpm': self.bpm,
            'previous_hash': self.previous_hash,
            'plc_data': self.plc_data,
            'validator': validator_dict,
        }
        return json.dumps(block_dict, sort_keys=True)
    
    
    def to_list(self):
        return [self.indx, self.bpm, self.timestamp, self.previous_hash, self.plc_data, int(self.validator.to_list()[0])]

class Validator():
    def __init__(self, ip, tokens, age):
        self.creation_time = time.time()
        self.ip = ip
        self.tokens = tokens
        self.age = age
        
    def to_dict(self):
        return {'ip': self.ip, 'tokens': self.tokens, 'age': self.age}
    
    def to_string(self):
        return json.dumps(self.to_dict())
    
    def to_list(self):
        return [self.ip, self.tokens, self.age]

class Blockchain:

    def __init__(self):
        self.chain = []
        self.repository = []
        self.start_genesis_block()
        self.start_genesis_box()
        self.index = 0
        self.validators = set()
        self.temporaryBlocks = []

    def start_genesis_box(self):
        genesis_box =  Box([Block(0, 1, str(datetime.datetime.now().replace(microsecond=0)), '0', '0'*32, Validator(1, 1, 1)),
                           Block(0, 1, str(datetime.datetime.now().replace(microsecond=0)), '0', '0'*32, Validator(1, 1, 1)),
                           Block(0, 1, str(datetime.datetime.now().replace(microsecond=0)), '0', '0'*32, Validator(1, 1, 1)),
                           Block(0, 1, str(datetime.datetime.now().replace(microsecond=0)), '0', '0'*32, Validator(1, 1, 1)),
                           Block(0, 1, str(datetime.datetime.now().replace(microsecond=0)), '0', '0'*32, Validator(1, 1, 1))], 0, 1, str(datetime.datetime.now().replace(microsecond=0)))
        self.repository.append(genesis_box)
        return genesis_box
    
    def start_genesis_block(self):
        """ initial blockchain block, with an index and a previous hash of 0"""
        genesis_block = Block(0, 1, datetime.datetime.now().replace(microsecond=0), '0', '0'*32, Validator(1, 1, 1))
        self.chain.append(genesis_block) 
        return genesis_block
    
    def create_block(self, bpm, plc_data, validator, session):
        """
        Creates a temporary block to be validated
        """
        previous_hash = self.chain[-1].compute_hash()
        block = Block(self.index +1, bpm, datetime.datetime.now(), previous_hash , plc_data, validator)
        self.temporaryBlocks.append(block)
        return block
    
    def add_blocks(self, block):
        """
        Clears the temporary blocks and adds the block to the chain
        """
        self.temporaryBlocks = []
        self.index += 1
        with app.app_context():
            session.add(block)
            session.commit()
            session.refresh(block)
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
        chosen_block = None
        chosen_validator = self.select_winner()
        while chosen_validator == None:
            chosen_validator = self.select_winner()
        
        for block in self.temporaryBlocks:
            validator = block.get_validator()
            if validator.ip == chosen_validator.ip:
                chosen_block = block
                validator.tokens += chosen_block.bpm/50
                break   
            
        self.add_blocks(chosen_block)
        return chosen_block

    
    def compute_hash(self):
        for block in self.blocks:
            block_string += block.to_string()
        block_string += self.nounce
        return sha256(block_string.encode()).hexdigest()
    
    def proof_of_work(self):
        blocks = self.chain[-5:]
        nounce = 1
        check_nounce = False
        previous_hash = self.repository[-1].compute_hash()
        current_size = len(self.chain)
        while check_nounce is False:
            caixa = Box(blocks, previous_hash, nounce, str(datetime.datetime.now().replace(microsecond=0)))
            hash_operation = caixa.compute_hash()
            if hash_operation[:zeros_in_hash] == '0'*zeros_in_hash:
                check_nounce = True
            else:
                nounce = randint(2, 10**10)

            if len(self.chain) > current_size:
                break

        self.repository.append(caixa)
        return self.repository
            
    def simulate_attack(self):
        target = randint(1, len(self.chain)-1)
        previous_data = self.chain[target].plc_data
        new_data = [1,1,1,1,1,1,1,1,1]
        self.chain[target].plc_data= new_data
        
        return target, previous_data, new_data
        
def background():
    ''' creating a new block in the background every 30 seconds'''
    
    current_time = time.time()
    while True:
        new_time = time.time()
        plc_str = convert_dict_to_str(plc_data)
        if (new_time - current_time >= background_timer1) or check_plc_data(plc_str):
            block_bpm = randint(10,50)
            
            for validator in blockchain.validators:
                time_now = time.time()
                validator.age = int(time_now - validator.creation_time)
                session = create_session()
                blockchain.create_block(block_bpm, plc_str, validator, session)
                
            blockchain.proof_of_stake()
            current_time = new_time

    
def background_2():
    #current_time = time.time()
    while True:
        #new_time = time.time()
        #if (new_time - current_time >= 300): 
            
        blockchain.proof_of_work()
            #current_time = new_time
        
         
def convert_dict_to_str(plc_dict):
    pcs = len(plc_dict)
    lst_of_dcts = list(plc_dict.values())
    plc_str = ''
    for i in range(pcs):
        for data in list(lst_of_dcts[i].values()):
            data = str(data)
            plc_str += data
    return plc_str

def check_plc_data(data_plc):
    last_block = session.query(Block).order_by(Block.indx.desc()).first()
    last_data = last_block.get_plc_data()
    if data_plc == "":
        return False
    if data_plc == last_data:
        return False
    return True
    

blockchain = Blockchain()

#app = Flask(__name__)

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
        ip = request.form["ip"]
        tokens = request.form["tokens"]
        
        new_validator = Validator(str(ip), int(tokens), 1)
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

@app.route('/remove_validator', methods=['GET', 'POST'])
def remove_validator():
    if request.method == 'POST':
        ip = request.form['ip']
        blockchain.remove_validator(ip)
        
        return render_template('remove validator.html')
    return render_template('remove validator.html')

@app.route('/data', methods=['POST'])
def receive_data():
    # Extract the data and source IP from the request
    data = request.get_json()
    source_ip = request.remote_addr
    
     # If we haven't received data from this source before, create a new list
    if source_ip not in plc_data:
        ip = source_ip.replace('.', '')
        blockchain.add_validator(Validator(ip, 1, 1))
        plc_data[source_ip] = ""
    
    # Add the data to the list of PLC data for this source
    plc_data[source_ip] = data
    print(plc_data)
    
    # Return a response to indicate success
    return {'status': 'success'}


@app.route('/display_boxes', methods=['GET'])
def display_boxes():
    
    headings = ("First Block","Last Block", "Previous Hash", "Nounce", "Timestamp")
    boxes = []
    
    for box in reversed(blockchain.repository):
        boxes.append(box.to_list())

    return render_template('display boxes.html', boxes = boxes, headings = headings)

@app.route('/simulate_attack', methods=['GET'])
def simulate_attack():
    attack = blockchain.simulate_attack()
    
    target = attack[0]
    previous_data = attack[1]
    new_data = attack[2]
    
    return render_template('simulate attack.html', target=target, previous_data=previous_data, new_data=new_data)


@app.route('/check_validation', methods=['GET'])
def checks_if_valid():
    status = blockchain.check_if_valid(blockchain.chain)
    
    return render_template('check validation.html', status=status)


thread = Thread(target = background)
thread2 = Thread(target = background_2)
thread.start()
thread2.start()


if __name__ == '__main__':
    # Garanta que as tabelas sejam criadas somente quando o arquivo for executado diretamente
    with app.app_context():
        db.create_all()
        db.session.commit()
    app.run(host=my_ip, port=5000, threaded=True)
