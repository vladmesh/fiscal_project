import aiohttp.web

from fiscal_api_service.ax.views import get_cashbox_data

urls = [aiohttp.web.get('/cashbox/', get_cashbox_data),
        aiohttp.web.post('/cashbox/register', reg_cashbox),
        aiohttp.web.post('/cashbox/close_fn', close_fn), ]
