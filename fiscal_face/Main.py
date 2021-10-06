from aiomisc import entrypoint

from fiscal_api_service.aiohttp_server import REST
from fiscal_api_service.PeriodicTasks import FiscalPeriodic

rest_service = REST(address='10.2.50.29', port=8082)
fiscal_service = FiscalPeriodic(interval=5*60)
services = [rest_service, fiscal_service]

with entrypoint(*services) as loop:
    loop.run_forever()
