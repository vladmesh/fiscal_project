import aiohttp.web
from aiomisc.service.aiohttp import AIOHTTPService

from core.entities import Cashbox
from core.entities.Ofd import Ofd
from fiscal_service.CashboxSender import CashboxSender


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

        app.add_routes([
            aiohttp.web.get('/ticket/', get_ticket_by_uid),
            aiohttp.web.post('/ticket', post_ticket),

        ])

        return app
