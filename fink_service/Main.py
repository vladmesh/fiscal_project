from aiomisc import entrypoint
from SourcePeriodic import construct
from fink_aiohttp_server import REST

rest_service = REST(address='localhost', port=8082)


with entrypoint(*services) as loop:
    loop.run_forever()
