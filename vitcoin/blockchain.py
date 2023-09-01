import asyncio
import math
import json
import structlog
import random
from hashlib import sha256
from time import time

logger = structlog.getLogger('blockchain')


class Blockchain:
	def __init__(self):
		self.chain = []
		self.pending_transactions = []
		self.target = '0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'

		logger.info('Creating genesis block')

		self.chain.append(self.new_block())

	def new_block(self):
		block = self.create_block(
			height=len(self.chain),
			transactions=self.pending_transactions,
			previous_hash=self.last_block['hash'] if self.last_block else None,
			nonce=format(random.getrandbits(64), 'x'),
			target=self.target,
			timestamp=time()
		)

		self.pending_transactions = []

		return block

	@staticmethod
	def create_block(height, transactions, previous_hash, nonce, target, timestamp=None):
		block = {
			'height': height,
			'transactions': transactions,
			'previous_hash': previous_hash,
			'nonce': nonce,
			'target': target,
			'timestamp': timestamp or time()
		}

		block_string = json.dumps(block, sort_keys=True).encode()
		block['hash'] = sha256(block_string).hexdigest()

		return block

	@staticmethod
	def get_hash(block):
		block_string = json.dumps(block, sort_keys=True).encode()

		return sha256(block_string).hexdigest()

	@property
	def last_block(self):
		return self.chain[-1] if self.chain else None

	def validate_block(self, block):
		return block['hash'] < self.target

	def add_block(self, block):
		self.chain.append(block)

	def recalculate_target(self, block_index):
		if not block_index % 10:
			expected_timespan = 10 * 10

			actual_timespan = self.chain[-1]['timestamp'] - self.chain[-10]['timestamp']

			ratio = actual_timespan / expected_timespan

			ratio = max(0.25, ratio)
			ratio = min(4.00, ratio)

			new_target = int(self.target, 16) * ratio
			
			self.target = format(math.floor(new_target), 'x').zfill(64)

			logger.info(f'Calculated new mining target: {self.target}')

		return self.target

		async def get_blocks_after_timestamp(self, timestamp):
			for index, block in enumerate(self.chain):
				if timestamp < block['timestamp']:
					return self.chain[index:]

		async def mine_new_block(self):
			self.recalculate_target(self.last_block['index'] + 1)

			while True:
				new_block = self.new_block()

				if self.validate_block(new_block):
					break

				await asyncio.sleep(0)

			self.chain.append(new_block)

			logger.info('A new block was found:', new_block)
