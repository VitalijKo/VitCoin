import asyncio
from vitcoin.blockchain import Blockchain
from vitcoin.connections import ConnectionPool
from vitcoin.peers import P2PProtocol
from vitcoin.server import Server

blockchain = Blockchain()
connection_pool = Blockchain()
server = Server(blockchain, connection_pool, P2PProtocol)


async def main():
	await server.listen()


asyncio.run(main())
