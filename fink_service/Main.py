import logging
from aiomisc.log import basic_config
from aiomisc import entrypoint
from FinkPeriodic import FinkPeriodic
from fink_aiohttp_server import REST

basic_config(level=logging.DEBUG, buffered=True)
rest_service = REST(address='0.0.0.0', port=8086)
periodic_service = FinkPeriodic(interval=6*60)


with entrypoint(rest_service, periodic_service) as loop:
    loop.run_forever()
