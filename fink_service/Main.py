from aiomisc import entrypoint

from core.asyncdb import FinkHelper
from SourcePeriodic import construct
from fink_aiohttp_server import REST

rest_service = REST(address='localhost', port=8082)
fink_helper = FinkHelper()
services = [rest_service]
asuop_settings = fink_helper.get_sources_settings()
for sett in asuop_settings:
    source_periodic = construct(sett)
    services.append(source_periodic)

with entrypoint(*services) as loop:
    loop.run_forever()
