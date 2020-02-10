# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 19:28:46 2020

@author: vipul
"""
# Module 1 - Create a Blockchain
import datetime  #Each block will have own time stamp
import hashlib   #Hash the blocks
import json      #Encode the block before we hash them
from flask import Flask, jsonify  #Web application, return messages in postman when we interact with blockchain
#index of new block, proof of new block and previous hash attached

# Part 1 - Building a Blockchain
class Blockchain:                           #1
    #all pilars of block chain
    #We create genesis block
    #Initialize a chain that will be in the function
    #Make create block function to add a new block to be mined later
    #Define module to create a solid block i.e which can't be hacked
    def __init__(self):  #2   #self is reffered to a object in a class
        self.chain = []  #Initialize the chain as list containing diff. block
        self.create_block(proof = 1, previous_hash = '0') 
        #Initialize the Block as genesis block
        #With this call the future function to be made
        #We will create a function for genesis block that will call create block method
    
    #Create a create _block function to get this genesis block as well as able to
    #create the next block once they are mined. 
    #understand difference btw create block and future 9 block function that we will
    #made at the end of this
    
    #We apply create_block function right after mining a block
    #The mine_block function will simply get the porof of work that we all need to solve
    #So we will define problem and define the algo to find that proof of work
    #Once we find that proof of work that means a new block is mine
    #Then we create a new block and added to blockchain
    
    #it will not only create a block with features like index, timestamp, proof, previous hash
    #but also will append this new mined block to the block chain
    
    #arguments-self, proof as will be created right after block mined so need proof of work
    #proof will be found by using mine_block function to be created
    def create_block(self, proof, previous_hash):
        #Define dict. for essential keys of a block
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,             #we will create pr0of of work function that will 
                                             #return exactly the new proof of a new 
                                             #block that we mine
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block
    #this create_block function will be used right after solving the proof of work
    #right after mining some block
    #i.e. this block will be used after future functions
    
    #Get the last block of the current block chain
    def get_previous_block(self):
        return self.chain[-1]
    
    #proof of work is a no. that a miner needs to mine in order to mine a new block
    #problem will be tuff to solve and easy to verify
    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    #Has the block of block chain
    #dumps function will take the values given in dict. of create_block func. and generate string
    #in next part we will put our dict. in json file so we need dumps func.
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    #It will return true if everything in our blk chain is right i.e each block is having valid proof of work
    #Two things to be chked 1st is previous hash of each block==hash of prev. blk
    ##2nd to chk proof of each blk is valid acc. to proof of work
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    
# Part 2 - Mining our Blockchain

# Creating a Web App
app = Flask(__name__)

# Creating a Blockchain by creating 1st instance or object of blockchain class
blockchain = Blockchain()

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200


# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5000)
