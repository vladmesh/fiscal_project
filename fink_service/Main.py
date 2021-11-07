from aiomisc import entrypoint
from FinkPeriodic import FinkPeriodic
from fink_aiohttp_server import REST

rest_service = REST(address='localhost', port=8082)
periodic_service = FinkPeriodic(interval=6*60)


with entrypoint(rest_service, periodic_service) as loop:
    loop.run_forever()
