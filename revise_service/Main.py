from aiomisc import entrypoint

from server.aiohttp_server import REST

rest_service = REST(address='0.0.0.0', port=8085)
services = [rest_service]

with entrypoint(*services) as loop:
    loop.run_forever()
