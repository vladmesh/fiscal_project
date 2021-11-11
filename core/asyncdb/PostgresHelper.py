import logging

import aiopg as aiopg

from core.entities.Enums import DocumentType
from core.entities.entities import Document, Ticket, Company
from core.sources.entities import SourceTicket, SourceDocument


class PostgresAsyncHelper:
    def __init__(self, host, dbname, user, password, port=5432):
        self.dsn = f'dbname={dbname} user={user} password={password} host={host} port={port}'

    async def execute_query(self, query, has_result=True):
        answer = None
        async with aiopg.create_pool(self.dsn, timeout=1500) as pool:
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
    # TODO по хорошему, весь этот код должен быть внутри джанго и вызываться через http
    def __init__(self):
        super().__init__(host='10.2.50.17', user='fiscal', password='fiscal', dbname='fiscaldb_new', port=5433)

    async def get_documents_by_date_fiscal(self, date_from, date_to, companies):
        documents = set()
        companies_str = ','.join(f"'{x.inn + x.kpp}'" for x in companies if x.ofd_login and x.ofd_password)
        companies_str = f'({companies_str})'
        if companies_str == '()':
            return documents
        command = f"set timezone = 'utc'; select d.id, fn_number, fiscal_number, fiscal_sign, session_num," \
                  f" num_in_session, date_fiscal, price, additional_prop, tickets_tax.name as tax_name," \
                  f" tickets_vat.name as vat_name," \
                  f" ticket_id, type_id, payment_type, inn, kpp " \
                  f"from public.tickets_fiscaldocument d " \
                  f"join public.tickets_company on ( " \
                  f"tickets_company.id = d.company_id) " \
                  f"join public.tickets_tax on (tickets_tax.id = d.tax_id) " \
                  f"join public.tickets_vat on (tickets_vat.id = d.vat_id) " \
                  f"where date_fiscal >= '{date_from}' and date_fiscal < '{date_to}' and CONCAT(inn, kpp) in {companies_str}"
        rows = await self.execute_query(command)
        for row in rows:
            document = SourceDocument(row)
            document.company_id = [x for x in companies if x.inn == document.inn and x.kpp == document.kpp][0].id
            documents.add(document)
        return documents

    async def get_tickets_by_date_ins(self, date_from, date_to, companies):
        tickets = set()
        companies_str = ','.join(f"'{x.inn + x.kpp}'" for x in companies)
        companies_str = f'({companies_str})'
        command = f"set timezone = 'utc'; select t.id, ticket_number, ticket_series, date_trip, " \
                  f"date_ins_asuop, payment_type, price, tickets_tax.name as tax_name," \
                  f" tickets_vat.name as vat_name, inn, kpp " \
                  f"from public.tickets_fiscalticket t " \
                  f"join public.tickets_company on ( " \
                  f"tickets_company.id = t.company_id) " \
                  f"join public.tickets_tax on (tickets_tax.id = t.tax_id) " \
                  f"join public.tickets_vat on (tickets_vat.id = t.vat_id) " \
                  f"where date_ins_asuop >= '{date_from}' and date_ins_asuop < '{date_to}' " \
                  f"and CONCAT(inn, kpp) in {companies_str}"
        rows = await self.execute_query(command)
        for row in rows:
            ticket = SourceTicket(row)
            ticket.company_id = [x for x in companies if x.inn == ticket.inn and x.kpp == ticket.kpp][0].id
            tickets.add(ticket)
        return tickets

    async def insert_ticket(self, ticket: Ticket):
        command = "INSERT INTO public.tickets_fiscalticket(date_create,  ticket_number, ticket_series, " \
                  "date_trip, date_ins_asuop, date_ins_sf, payment_type, price, company_id, " \
                  f"payment_option_id, tax_id, vat_id)  VALUES(now(), '{ticket.ticket_number}', " \
                  f"'{ticket.ticket_series}', '{ticket.date_trip}', '{ticket.date_ins}', null , " \
                  f"{ticket.payment_type.value}, {ticket.price}, {ticket.company_id}, null, {ticket.tax}, " \
                  f"{ticket.vat});"
        await self.execute_query(command, False)

    async def insert_document(self, document: Document):
        command = "INSERT INTO public.tickets_fiscaldocument(date_create, fn_number, fiscal_number, fiscal_sign, " \
                  "session_num, num_in_session, date_fiscal, date_ins_sf, price, additional_prop, " \
                  " is_storned,  company_id, tax_id,  type_id, vat_id, payment_type) " \
                  f"VALUES (now(), {document.fn_number}, {document.fiscal_number}, " \
                  f"{document.fiscal_sign}, {document.session_num}, {document.num_in_session}, " \
                  f"'{document.date_fiscal}', null, {document.price}, null, false, {document.company_id}, " \
                  f"{document.tax}, {document.type.value}, {document.vat}, " \
                  f"{document.payment_type.value});"
        await self.execute_query(command, False)

    async def get_company_id_by_inn_kpp(self, inn, kpp):
        command = f"select id from public.tickets_company where inn = '{inn}' and kpp = '{kpp}' "
        rows = await self.execute_query(command)
        if len(rows) == 0:
            return None
        return rows[0]['id']

    async def get_companies_by_region(self, region_id):
        command = f"select * from public.tickets_company where region_id = '{region_id}' "
        rows = await self.execute_query(command)
        if len(rows) == 0:
            return None
        answer = []
        for row in rows:
            answer.append(Company(**row))
        return answer

    async def get_region_id_by_name(self, region_name):
        command = f"select id from public.tickets_region where name = '{region_name}'"
        rows = await self.execute_query(command)
        if len(rows) == 0:
            return None
        return rows[0]['id']

    async def get_tickets_without_docs(self):
        answer = []
        command = "select company_id, id as dbf_id, vat_id as vat, tax_id as tax, date_trip, price, payment_type" \
                  " from tickets_fiscalticket t where not exists " \
                  "(select 1 from tickets_fiscaldocument d where " \
                  "d.ticket_id = t.id)"
        rows = await self.execute_query(command)
        for row in rows:
            ticket = Ticket(**row)
            answer.append(ticket)
        return answer

    async def get_document_for_ticket(self, ticket: SourceTicket, need_date):
        command = f"select * from tickets_fiscaldocument d " \
                  f"where d.company_id = {ticket.company_id} and d.vat_id = {ticket.vat} " \
                  f"and d.tax_id = {ticket.tax} and d.price = {ticket.price} " \
                  f"and d.payment_type = {ticket.payment_type} and d.ticket_id is null " \
                  f"and is_storned = false and type_id in (1,8) "
        if need_date:
            command += f" and d.date_fiscal > '{ticket.date_trip}'"
        rows = await self.execute_query(command)
        if len(rows) == 0:
            return None
        return SourceDocument(rows[0])

    async def bind_doc_to_ticket(self, doc: SourceDocument, ticket: Ticket):
        command = f"update tickets_fiscaldocument set ticket_id = {ticket.dbf_id} where id = {doc.id}"
        await self.execute_query(command, False)

    async def remove_ticket(self, ticket):
        command = f"delete from tickets_fiscalticket where id = {ticket.dbf_id}"
        await self.execute_query(command, False)

    async def remove_documents_without_tickets(self):
        command = "delete from public.tickets_fiscaldocument where type_id in (1,8) and is_storned = false " \
                  "and ticket_id is null"
        await self.execute_query(command, False)

    async def get_max_date_ins_for_source(self, ax_source_id):
        command = "select max(date_ins_asuop) as max_date from public.tickets_fiscalticket where source_id = " \
                  f"(select id from public.tickets_source where ax_id = '{ax_source_id}')"
        rows = await self.execute_query(command)
        if len(rows) == 0 or 'max_date' not in rows[0]:
            return None
        return rows[0]['max_date']


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
                  f"{document.fn_number}, '{document.date_fiscal}', {document.type.value}, " \
                  f"{document.ticket_id})"
        await self.execute_query(command, False)
