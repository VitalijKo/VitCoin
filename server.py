import asyncio
import structlog
from marshmallow.exceptions import MarshmallowError
from vitcoin.messages import BaseSchema
from vitcoin.utils import get_external_ip

logger = structlog.getLogger()


class Server:
	def __init__(self, blockchain, connection_pool, p2p_protocol):
		self.blockchain = blockchain
		self.connection_pool = connection_pool
		self.p2p_protocol = p2p_protocol
		self.external_ip = None
		self.external_port = None

		if not (blockchain and connection_pool and p2p_protocol):
			logger.error(
				"All of 'blockchain', 'connection_pool', and 'gossip_protocol' must be provided"
			)

			raise Exception('Could not start')

	async def get_external_ip(self):
		self.external_ip = await get_external_ip()

	async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
		while True:
			try:
				data = await reader.readuntil(b'\n')

				decoded_data = data.decode().strip()

				try:
					message = BaseSchema.loads(decoded_data)
				except MarshmallowError:
					logger.info('Received unreadable message', peer=writer)

					break

				writer.address = message['info']['address']

				self.connection_pool.add_peer(writer)

				await self.p2p_protocol.handle_message(message, writer)
				await writer.drain()

				if writer.is_closing():
					break
			except (asynco.exceptions.ImcompleteError, ConnectionError):
				break

		writer.close()

		await writer.wait_closed()

		self.connection_pool.remove_peer(writer)

	async def listen(self, hostname='0.0.0.0', port=1101):
		server = await asyncio.start_server(self.handle_connection, hostname, port)

		logger.info(f'The server is listening on port {hostname}:{port}')

		self.external_ip = await self.get_external_ip()
		self.external_port = port

		async with server:
			await server.serve_forever()
