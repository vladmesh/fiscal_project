import aiopg as aiopg

from core.entities.Enums import Tax, Vat, PaymentType, DocumentType
from core.entities.entities import Document, Ticket
from revise_service.entities import ReviseTicket, ReviseDocument


class PostgresAsyncHelper:
    def __init__(self, host, dbname, user, password, port=5432):
        self.dsn = f'dbname={dbname} user={user} password={password} host={host} port={port}'

    async def execute_query(self, query, has_result=True):
        answer = None
        async with aiopg.create_pool(self.dsn) as pool:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query)
                    if has_result:
                        records = await cur.fetchall()
                        col_names = [x[0] for x in cur.description]
                        answer = [dict(zip(col_names, record)) for record in records]
                    cur.close()
        return answer


class PostgresHelperDbf(PostgresAsyncHelper):
    def __init__(self):
        super().__init__(host='10.2.50.17', user='fiscal', password='fiscal', dbname='fiscaldb_new', port=5433)

    async def get_documents_by_date_fiscal(self, date_from, date_to, region, timezone):
        documents = set()
        command = f"set timezone = '{timezone}'; select d.id, fn_number, fiscal_number, fiscal_sign, session_num," \
                  f" num_in_session, date_fiscal, price, additional_prop, tickets_tax.name as tax_name," \
                  f" tickets_vat.name as vat_name," \
                  f" ticket_id, type_id, payment_type, inn, kpp " \
                  f"from public.tickets_fiscaldocument d " \
                  f"join public.tickets_company on (region_id = {region} and " \
                  f"tickets_company.id = d.company_id) " \
                  f"join public.tickets_tax on (tickets_tax.id = d.tax_id) " \
                  f"join public.tickets_vat on (tickets_vat.id = d.vat_id) " \
                  f"where date_fiscal >= '{date_from}' and date_fiscal < '{date_to}' "
        rows = await self.execute_query(command)
        for row in rows:
            documents.add(ReviseDocument(row))
        return documents

    async def get_tickets_by_date_ins(self, date_from, date_to, region, timezone):
        tickets = set()
        command = f"set timezone = '{timezone}'; select t.id, ticket_number, ticket_series, date_trip, " \
                  f"date_ins_asuop, payment_type, price, tickets_tax.name as tax_name," \
                  f" tickets_vat.name as vat_name, inn, kpp " \
                  f"from public.tickets_fiscalticket t " \
                  f"join public.tickets_company on (region_id = {region} and " \
                  f"tickets_company.id = t.company_id) " \
                  f"join public.tickets_tax on (tickets_tax.id = t.tax_id) " \
                  f"join public.tickets_vat on (tickets_vat.id = t.vat_id) " \
                  f"where date_ins_asuop >= '{date_from}' and date_ins_asuop < '{date_to}' "
        rows = await self.execute_query(command)
        for row in rows:
            tickets.add(ReviseTicket(row))
        return tickets


class PostgresHelperDev(PostgresAsyncHelper):
    """Для разработки протокола"""

    def __init__(self):
        super().__init__(host='10.2.50.35', user='postgres', password='qwerty',
                         dbname='fiscal_dev')

    async def insert_ticket_dev(self, ticket):
        command = f"INSERT INTO dbo.tickets( " \
                  f"ticketseries, ticketnumber, price, status, " \
                  f"lastupdate, dateins, paymenttype, datetrip, tax, vat, " \
                  f"datecreate, companyid, client_email)" \
                  f"VALUES ('{ticket.ticket_series}', '{ticket.ticket_number}', {ticket.price}, 0, now(), now()," \
                  f" {ticket.payment_type}, '{ticket.payment_date}',  'SIMPEXP', 'NONDS', now(), 1, " \
                  f"'{ticket.client_email}')"
        await self.execute_query(command, False)

    async def get_unimported_documents(self):
        command = f"select * from dbo.documents  join dbo.sessions on " \
                  f"(sessions.sessionid = documents.sessionid) join dbo.tickets on " \
                  f"(tickets.ticketid = documents.ticketid) where sent_to_fiscaldb = false"
        rows = await self.execute_query(command)
        answer = []
        for row in rows:
            document_dict = {}
            document_dict['id'] = row['documentid']
            document_dict['fiscal_date'] = row['documentdate']
            document_dict['fiscal_sign'] = row['fiscalsign']
            document_dict['fiscal_storage_number'] = row['fiscalstoragenum']
            document_dict['fiscal_number'] = row['fiscalnum']
            document_dict['document_type'] = DocumentType.receipt
            document_dict['ticket_id'] = row['ticketnumber']
            document = Document(**document_dict)
            answer.append(document)
        return answer

    async def set_doc_imported(self, document_id):
        command = f"update dbo.documents set sent_to_fiscaldb = True where documentid = {document_id}"
        await self.execute_query(command, False)


class PostgresHelperTmp(PostgresAsyncHelper):
    def __init__(self):
        super().__init__(host='localhost', dbname='tickets', user='postgres', password='postgres', port=5432)

    async def insert_ticket(self, ticket: Ticket):
        command = f"INSERT INTO dbo.tickets(ticket_series, ticket_number, client_email, price, vat, " \
                  f"tax, payment_type, company_id, payment_date) VALUES('{ticket.ticket_series}', " \
                  f"'{ticket.ticket_number}', " \
                  f"'{ticket.client_email}', {ticket.price}, {ticket.vat.value}, {ticket.tax.value}, " \
                  f"{ticket.payment_type.value}, '{ticket.company_id}', '{ticket.payment_date}')"
        await self.execute_query(command, False)

    async def get_ticket(self, ticket_number: str):
        command = f"SELECT * from dbo.tickets where ticket_number = '{ticket_number}'"
        rows = await self.execute_query(command)
        if len(rows) == 0:
            return None
        record = rows[0]
        ticket = Ticket(**record)
        return ticket

    async def insert_error(self, error, request: str):
        command = f"insert into dbo.errors(text, type, date_create, full_request) " \
                  f"VALUES('{error.text}', {error.type.value}, now(), '{request}') RETURNING id"
        rows = await self.execute_query(command)
        return rows[0]['id']

    async def get_document(self, ticket_id: str):
        command = f"SELECT * from dbo.documents where ticket_id = {ticket_id}"
        rows = await self.execute_query(command)
        if len(rows) == 0:
            return None
        if len(rows) > 1:
            raise Exception("Дубли документов")
        record = rows[0]
        document = Document(**record)
        return document

    async def get_unfiscal_tickets(self) -> list:
        command = "select * from dbo.tickets t where not exists (select 1 from dbo.documents d " \
                  "where d.ticket_id = t.id)"
        rows = await self.execute_query(command)
        answer = []
        for row in rows:
            ticket = Ticket(**row)
            answer.append(ticket)
        return answer

    async def insert_document(self, document: Document):
        command = f"insert into dbo.documents(fiscal_number, fiscal_sign, fiscal_storage_number, " \
                  f"fiscal_date, document_type, ticket_id) VALUES({document.fiscal_number}, {document.fiscal_sign}, " \
                  f"{document.fiscal_storage_number}, '{document.fiscal_date}', {document.document_type.value}, " \
                  f"{document.ticket_id})"
        await self.execute_query(command, False)
