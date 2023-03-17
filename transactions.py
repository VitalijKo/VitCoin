import json
from time import time
from nacl.encoding import HexEncoder
from nacl.exceptions import BadSignatureError
from nacl.signing import SigningKey, VerifyKey


def create_transaction(private_key, public_key, receiver, amount):
	tx = {
		'sender': public_key,
		'receiver': receiver,
		'amount': amount,
		'timestamp': int(time())
	}

	tx_bytes = json.dumps(tx, sort_keys=True).encode('ascii')

	signing_key = SigningKey(private_key, encoder=HexEncoder)

	signature = signing_key.sign(tx_bytes).signature

	tx['signature'] = HexEncoder.encode(signature).decode('ascii')

	return tx


def validate_transaction(tx):
	public_key = tx['sender']

	signature = tx.pop('signature')

	signature_bytes = HexEncoder.decode(signature)

	tx_bytes = json.dumps(tx, sort_keys=True).encode('ascii')

	verify_key = VerifyKey(public_key, encoder=HexEncoder)

	try:
		verify_key.verify(tx_bytes, signature_bytes)

		return True
	except BadSignatureError:
		return False
