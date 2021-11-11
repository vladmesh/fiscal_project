import aiohttp.web
from aiomisc.service.aiohttp import AIOHTTPService

import server.atol.urls
import server.ax.urls
import server.admin.urls


class REST(AIOHTTPService):
    async def create_application(self):
        print('init_rest')
        app = aiohttp.web.Application()
        urls = server.atol.urls.urls + server.ax.urls.urls + server.admin.urls.urls
        app.add_routes(urls)
        print('end_init_rest')

        return app
