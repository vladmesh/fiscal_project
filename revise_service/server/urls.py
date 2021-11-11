import aiohttp.web

from .views import start_revise, ping, load_dbf_tickets, load_dbf_documents, bind_documents

urls = [aiohttp.web.post('/revise/start', start_revise),
        aiohttp.web.post('/load_dbf_tickets', load_dbf_tickets),
        aiohttp.web.post('/load_dbf_documents', load_dbf_documents),
        aiohttp.web.post('/bind', bind_documents),
        aiohttp.web.get('/ping', ping)
        ]
