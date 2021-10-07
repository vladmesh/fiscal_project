import aiohttp.web

from views import close_fn, register_cashbox, get_cashbox_data

urls = [
    aiohttp.web.post('/close_fn', close_fn),
    aiohttp.web.post('/register_cashbox', register_cashbox),
    aiohttp.web.post('/get_cashbox_data', get_cashbox_data)
]
