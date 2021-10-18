from aiomisc import entrypoint

from fiscal_face.PeriodicTasks import FiscalPeriodic
from fiscal_face.server.aiohttp_server import REST

rest_service = REST(address='10.2.50.29', port=8082)
fiscal_service = FiscalPeriodic(interval=5*60)
services = [rest_service, fiscal_service]

with entrypoint(*services) as loop:
    loop.run_forever()
