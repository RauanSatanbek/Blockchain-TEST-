from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain.blockchain import Blockchain

# Создаем икземплярнашего узла
app = Flask(__name__)

# Генерируем уникальный адрес для нашего узла
node_identifier = str(uuid4()).replace('-', '')

# Создаем экзеипляр Blockchain
blockchain = Blockchain()

@app.route('/', methods=['GET'])
def index():
    return 'Our very first REAL BLOCKCHAIN!!!'

@app.route('/mine', methods=['GET'])
def mine():
    # Запускаем алгоритм PoW для того чтобы найти proof ...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)


    # Мы должны получить награду за найденный proof.
    # Если sender '0', то это означает что узел заработал токен.
    blockchain.new_transaction(
        sender='0',
        recipient=node_identifier,
        amount=1
    )

    block = blockchain.new_block(proof)

    response = {
        'message': 'New Block Forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Проверяем, что обзательное поля переданы в POST -запрос
    required = ['sender', 'recipient', 'amount']
    if not all(key in values for key in required):
        return 'Missing values', 400

    # Создаем новую транзакцию
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {
        'message': f'Transuction will be added to Block {index}'
    }

    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes has been added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET']
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
