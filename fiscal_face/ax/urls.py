import aiohttp.web

from fiscal_face.ax.views import reg_cashbox, get_cashbox_data, close_fn

urls = [aiohttp.web.get('/cashbox/', get_cashbox_data),
        aiohttp.web.post('/cashbox/register', reg_cashbox),
        aiohttp.web.post('/cashbox/close_fn', close_fn), ]
