# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 10:12:19 2020

@author: vipul
"""

#Add Transactions
#Create Decentralisation
import datetime  #Each block will have own timestamp
import hashlib  #Hash the block
import json   #Encode the block before we hash them
from flask import Flask, jsonify, request
#We will connect nodes in decentralised network using get_json which
#is available in request module

import requests
#it will be used to catch the right nodes when we check that all the
#nodes in d-cenerlised ntrk to apply consesnus.

from uuid import uuid4
from urllib.parse import urlparse
#It will create an address for each node in the ntrk and to parse the 
#URL of each of these nodes

#What makes a blockchain cryptocurrency?
#Transactions.
#1st pillar :- Transaction
#2nd pillar :- Consensus protocol

#Create a Blockchain
#Part 1:- Building the blockchain
class Blockchain:
    def __init__(self):
        self.chain=[]
        
        self.transactions = []
        self.create_block(proof=1,previous_hash='0')
        
        self.nodes = set()
        #not list as it will not be in a order being decentralised
        
    def create_block(self,proof,previous_hash):
        #Define Dict. for essential keys of block
        block = {'index':len(self.chain)+1,
                 'timestamp':str(datetime.datetime.now()),
                 'proof' :proof,
                 'previous_hash':previous_hash,
                 'transaction': self.transactions
                }
        self.transactions = []  #Transaction list must be empty after getting added to block
        self.chain.append(block)
        return block
    
    def get_previous_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, previous_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash_operation=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof=True
            else:
                new_proof += 1
        return new_proof
        
    def hash(self,block):
        encoded_block=json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self,chain):
        previous_block=chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation=hashlib.sha256(str(proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    #Create a format of Transaction
    #i.e. Format with Sender, Receiver, and Amount of coins exchanged
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender':sender,'receiver':receiver,'amount':amount})
        
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    #1st Pillar Complete
    
    
    #Create 2nd Pillar
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
     
    
    #Consensus Problem solve by replace method that will replace any
    #chain that is shorter than the longest chain among all the nodes
    #of network
    def replace_chain(self):
        network = self.nodes   #ntrk containing all the nodes
        max_length = len(self.chain)  #Length of chain of current node
        longest_chain = None   #to replace chain with longest chain
        
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
    
#Create a web app
app = Flask(__name__)  

node_address = str(uuid4()).replace('-','')

blockchain=Blockchain()  

#Part 2:- Mining of Blockchain
@app.route('/mine_block', methods=['GET'])
def mine_block():
    
    
    previous_block = blockchain.get_previous_block()
    
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address,receiver='Pavan',
                               amount=1)
    block = blockchain.create_block(proof, previous_hash)
    
    response = {'message':'Congrats, You mined a block',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof' : block['proof'],
                'previous_hash': block['previous_hash'],
                'transaction':block[ 'transaction']}
    return jsonify(response), 200

#Getting the chain of blocks
@app.route('/get_chain', methods=['GET'])
def get_chain():
    response = {'chain':blockchain.chain,
                'length':len(blockchain.chain)
                }
    return jsonify(response), 200

@app.route('/is_valid', methods=['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'Message':'The Chain is valid'}
    else:
        response = {'Message':'The Chain is not valid'}
    return jsonify(response), 200

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender','receiver','amount']
    if not all(key in json for key in transaction_keys):
        return 'Some elements are missing', 400
    index = blockchain.add_transaction(json['sender'],json['receiver'],
                               json['amount'])
    response = {'Message':f'This transaction will be added to block {index}'}
    return jsonify(response), 201

#Part 3:- Dentralisation

#Connect the available Nodes
@app.route('/connect_nodes', methods=['POST'])
def connect_nodes():
    json = request.get_json()  #returns json file with all the info of nodes
    nodes = json.get('nodes')  #we will pass exactly the key of which 
                                #to value is the address of nodes
    if nodes is None:
        return "No Nodes",400
    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message':'All nodes are now connected. the ITScoin Blockchain now contains following nodes:',
                'total nodes': list(blockchain.nodes)}
    return jsonify(response), 201

@app.route('/replace_chain', methods=['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response={"message":"The chain is replaces by largest one",
                  "new_chain":blockchain.chain}
    else:
        response=response={"message":"The chain is largest one",
                           "actual_chain":blockchain.chain}
    return jsonify(response), 200
#Run the app
app.run(host='0.0.0.0', port=5002)
