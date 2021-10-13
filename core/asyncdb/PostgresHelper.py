import aiopg as aiopg

from core.entities.Enums import Tax, Vat, PaymentType
from core.entities.entities import Ticket, Document


# from fiscal_face.atol.ErrorHandler import MegapolisApiError


class PostgresAsyncHelper:
    def __init__(self, host='localhost', dbname='tickets', user='postgres', password='postgres'):
        self.dsn = f'dbname={dbname} user={user} password={password} host={host}'

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

    async def insert_ticket(self, ticket: Ticket):
        command = f"INSERT INTO dbo.tickets(ticket_series, ticket_number, client_email, price, vat, " \
                  f"tax, payment_type, company_id) VALUES('{ticket.ticket_series}', " \
                  f"'{ticket.ticket_number}', " \
                  f"'{ticket.client_email}', {ticket.price}, {ticket.vat.value}, {ticket.tax.value}, " \
                  f"{ticket.payment_type.value}, '{ticket.company_id}')"
        await self.execute_query(command, False)

    async def get_ticket(self, ticket_number: str):
        command = f"SELECT * from dbo.tickets where ticket_number = '{ticket_number}'"
        rows = await self.execute_query(command)
        if len(rows) == 0:
            return None
        record = rows[0]
        ticket = Ticket(record['id'], record['ticket_series'], record['ticket_number'], record['price'],
                        PaymentType(record['payment_type']), record['client_email'], record['company_id'],
                        Tax(record['tax']), Vat(record['vat']))
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


async def main():
    ticket = Ticket(0, 'series', 'number', 11, PaymentType.CASH, 'email@email', 'company', Tax.GEN, Vat.NONDS)
    helper = PostgresAsyncHelper()
    await helper.insert_ticket(ticket)
    new_ticket = await helper.get_ticket('number')
    print(new_ticket.id)
