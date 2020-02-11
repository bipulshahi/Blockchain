# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 13:01:06 2020

@author: Pawan
"""
import datetime
import hashlib
import json
from flask import Flask, jsonify, request  #get_json will be used to connect nodes in decentralised system

import requests
#It will be used to catch the right nodes when we check that all
#the nodes in d-centralised ntrk to apply consesnus

from uuid import uuid4
from urllib.parse import urlparse
#It will create an address for each node in the ntrk and to parse the
#URL of ease of these nodes

#create a blockchain

class Blockchain:
    def __init__(self):
        self.chain = []
        
        self.transactions = []
        self.create_block(proof=1,previous_hash=0)
        
        self.nodes = set()
        
    def create_block(self,proof,previous_hash):
        #Define Dict. for essential keys of block
        block = {'index':len(self.chain)+1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof':proof,
                 'previous_hash':previous_hash,
                 'transaction':self.transactions}
        
        self.transactions = [] #Transaction list must be empty after added to the block
        self.chain.append(block)
        return block
        
    def get_previous_block(self):
        return self.chain[-1]
        
    def proof_of_work(self,previous_proof):
        new_proof = 1
        check_proof = False 
        while check_proof is False:
            hash_value=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_value[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self,block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self,chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            new_proof = block['proof']
            hash_value=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_value[:5] != '00000':
                return False
            
            previous_block = block
            block_index += 1
        return True
    
    #create a format of transaction
    #i.e. Format with Sender,Receiver, Amount
    def add_transaction(self,sender,receiver,amount):
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block = self.get_previous_block()
        return previous_block['index']+1
            
        
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
     
        
    def replace_chain(self):
        network = self.nodes  #all present nodes
        max_length = len(self.chain)  #Length of chain on current node
        longest_chain = None
        
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        
        if longest_chain:
            self.chain = longest_chain
            return True
        return False
        
        
        
        
        
        
        
        
        
        
        
        

app = Flask(__name__)
blockchain = Blockchain()

@app.route('/mine_block',methods=['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof,previous_hash)
    
    response = {'message':'block is mined',
                'index':block['index'],
                'timestamp':block['timestamp'],
                'proof':block['proof'],
                'previous_hash':block['previous_hash']}
    return jsonify(response), 200

@app.route('/get_chain',methods=['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length':len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid',methods=['GET'])
def is_valid():
    is_valid=blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message':'Your chain is validatted'}
    else:
        response = {'message':'Your chain is not valid'}
    return jsonify(response), 200

@app.route('/add_transaction',methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements are missing', 400
    index = blockchain.add_transaction(json['sender'],
                                       json['receiver'],
                                       json['amount'])
    response = {'Message':f'The transaction is added to block {index}'}
    return jsonify(response), 201

@app.route('/connect_nodes',methods=['POST'])
def connect_nodes():
    json = request.get_json()
    nodes = json.get('nodes')
    
    if nodes is None:
        return 'No Nodes',400
    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message':'all nodes are now connected',
                'Total nodes':list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain',methods=['GET'])
def replace_chain():
    is_chain = blockchain.replace_chain()
    if is_chain:
        response={"message":"The chain is replaced with longest one",
                  "New Udated chain":blockchain.chain}
    else:
        response = {"message":"It is longest one",
                    "actual_chain":blockchain.chain}
        
    return jsonify(response), 200
    
app.run(host='0.0.0.0',port = 5000)    
    
    
    