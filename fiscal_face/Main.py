import logging

from aiomisc import entrypoint
from aiomisc.log import basic_config

from face.PeriodicTasks import FiscalPeriodic
from server.aiohttp_server import REST

basic_config(level=logging.DEBUG, buffered=False)
logging.debug('begin')
rest_service = REST(address='0.0.0.0', port=8082)
fiscal_service = FiscalPeriodic(interval=5*65)

with entrypoint(rest_service, fiscal_service) as loop:
    loop.run_forever()
