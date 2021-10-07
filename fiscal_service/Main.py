from aiomisc import entrypoint

from fiscal_service.PeriodicTasks import FiscalPeriodic
from fiscal_service.aiohttp_server import REST

rest_service = REST(address='localhost', port=8083)
fiscal_service = FiscalPeriodic(interval=5*60)
services = [rest_service, fiscal_service]

with entrypoint(*services) as loop:
    loop.run_forever()
