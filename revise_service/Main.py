from aiomisc import entrypoint

from revise_service.server.aiohttp_server import REST

rest_service = REST(address='10.2.50.29', port=8085)
services = [rest_service]

with entrypoint(*services) as loop:
    loop.run_forever()
