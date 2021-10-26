import aiohttp.web

from fiscal_face.server.admin.views import load_dbf_tickets, load_dbf_documents, bind_documents

urls = [aiohttp.web.post('/load_dbf/tickets', load_dbf_tickets),
        aiohttp.web.post('/load_dbf/documents', load_dbf_documents),
        aiohttp.web.post('/bind', bind_documents)]
