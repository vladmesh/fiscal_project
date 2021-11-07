from aiomisc import entrypoint

from face.PeriodicTasks import FiscalPeriodic
from server.aiohttp_server import REST

rest_service = REST(address='localhost', port=8082)
fiscal_service = FiscalPeriodic(interval=5*60)
services = [rest_service, fiscal_service]

with entrypoint(*services) as loop:
    loop.run_forever()
