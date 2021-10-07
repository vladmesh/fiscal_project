import aiohttp.web
from aiomisc.service.aiohttp import AIOHTTPService

import fiscal_face.atol.urls
import fiscal_face.ax.urls


async def get_ticket_by_uid(request):
    params = request.rel_url.query
    print(params['uid'])
    return aiohttp.web.Response(text='f')


async def post_ticket(request):
    data = await request.json()
    print(data)


class REST(AIOHTTPService):
    async def create_application(self):
        app = aiohttp.web.Application()
        urls = fiscal_face.atol.urls.urls + fiscal_face.ax.urls.urls
        app.add_routes(urls)

        return app
