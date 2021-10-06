import aiohttp.web

from views import close_fn, register_cashbox

urls = [
    aiohttp.web.post('/close_fn', close_fn),
    aiohttp.web.post('/register_cashbox', register_cashbox)
]
