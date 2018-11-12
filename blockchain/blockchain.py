import hashlib
import json

from time import time
from urllib.parse import urlparse

class Blockchain(object):
    def __init__(self):
        """
        Инициализируем блокчейн
        """

        self.current_transactions = []
        self.chain = []

        # Create the genesis block
        self.new_block(proof=100, previous_hash='1')

    def new_block(self, proof, previous_hash=None):
        """
        Создаем новый блок в нашем блокчейне

        :параметр proof: <int> proof полученный после использования алгоритма «Доказательство выполнения работы»
        :параметр previous_hash: (Опциональный) <str> Хэш предыдущего блока
        :return: <dict> New block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash
        }

        # Сбрасываем текущий список транзакций
        self.current_transactions = []

        self.chain.append(block)

        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Создает новую транзакуию для перехода к следующему замайненому блоку

        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the recipient
        :param amount: <int> The transuction amount
        :return: Индекс блока который будет хранить в себу эту транзакцию
        """

        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }

        self.current_transactions.append(transaction)

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Создает SHA-256 хэш блока

        :param block: <dict> Block
        :return: <str>
        """

        block_string = json.dumps(block, sort_keys=True).encode()
        hash = hashlib.sha256(block_string).hexdigest()

        return hash

    def proof_of_work(self, last_proof):
        """
        Простой алгоритм PoW
        - Ищем число p' такое, чтобы hash(pp') содержал в себе 4 лидирующих нуля
        - p это предыдущи proof, p' это новый proof

        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof


    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Проверяем Proof: содержили ли hash(last_proof, proof) 4 лидирующих нуля?

        :param last_proof: <int> предыдущий Proof
        :param proof: <int> Текущий Proof
        :return: True если все верно, иначе False
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:4] == '0000'

    def register_node(self, address):
        """
        Добавляем новый узел в список узлов

        :param address: <str> Адрес узла, например 'http://192.168.0.5:5000'
        :return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, chain):
        """
        Определяем что данный блокчейн прошел проверку

        :param chain: <list> Blockchain
        :raturn: <bool> Truen если прошел проверку, а иначе False
        """
        last_block = chain[0]
        current_inedx = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print('/--* YiY *--/')

            # Проверяем, что хэш этого блока корректен
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Проверяем, что алгоритм PoW корректен
            if not self.valid_proof(last_block['proof'], block["proof"]):
                return False


            last_block = block
            current_index += 1


        return True

    def resolve_conflicts(self):
        """
        Это наш алгоритм Консенсуса, он разрешает конфликт путем
        замены нашей цепочки на самую длиную в сети.

        :return: <bool> True если наша цепочка было заменена, False если это не так.
        """

        neighbours = self.nodes
        new_chain = None

        # Мы ищем цепочки длинее наих.
        max_length = len(self.chain)


        # Берем все цепоцки со всех углов нашей сети и проверяем их
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            length = response.json()['length']
            chain = response.json()['chain']

            # Проверяем, что цепочка имеет
            # максимальную длину и она коректно
            if length > max_length and self.valid_chain(chain):
                max_length = max_length
                new_chain = chain

            # Заменяем нашу цепочку, если нашли другую,
            # Каторая имеет больше длину и является коректной
            if new_chain:
                self.chain = new_chain
                return True

            return False
