import json
import structlog
from nacl.encoding import HexEncoder
from nacl.signing import SigningKey

logger = structlog.getLogger(__name__)


def generate_wallet():
	private_key = SigningKey.generate()
	public_key = private_key.verify_key
	payload = {
		'private_key': private_key.encode(encoder=HexEncoder).decode(),
		'public_key': public_key.encode(encoder=HexEncoder).decode()
	}

	with open('wallet.json', 'w') as wallet_file:
		json.dump(payload, wallet_file)

	logger.info('New wallet generated: wallet.json')

	return payload


try:
	with open('wallet.json', 'r') as wallet_file:
		keys = json.load(wallet_file)

	logger.info('Keys loaded from wallet.json')
except (json.decoder.JSONDecodeError, FileNotFoundError):
	keys = generate_wallet()

PRIVATE_KEY = keys['private_key']
PUBLIC_KEY = keys['public_key']
