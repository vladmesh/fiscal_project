import psycopg2

from core.entities.Cashbox import Cashbox
from core.entities.Company import Company
from core.entities.Document import Document
from core.entities.Route import FinkRoute
from core.entities.Settings import Settings
import datetime as dt

from core.entities.Ticket import Ticket
from core.entities.sourcesettings import SourceSettings


class Region:
    def __init__(self, record):
        self.id = record['id']
        self.name = record['name']


class Tax:
    def __init__(self, record):
        self.id = record['id']
        self.name = record['name']


class Vat:
    def __init__(self, record):
        self.id = record['id']
        self.name = record['name']


class DbfCashbox:
    def __init__(self, record):
        if record:
            self.id = record['id']
            self.factory_number = record['factory_number']


class PostgresHelper:
    def __init__(self, dbname, user='postgres', password='postgres', host='localhost', port='5432'):
        self.host = host
        self.connection = None
        self.dbname = dbname
        self.user = user
        self.password = password
        self.port = port

    def openConnection(self):
        self.connection = psycopg2.connect(dbname=self.dbname, user=self.user,
                                           password=self.password, host=self.host, port=self.port)

    def closeConnection(self):
        self.connection.close()

    def executeCommand(self, command, has_result=True):
        records = []
        col_names = []
        self.openConnection()
        cursor = self.connection.cursor()
        cursor.execute(command)
        if has_result:
            records = cursor.fetchall()
            col_names = [x[0] for x in cursor.description]
        self.connection.commit()
        cursor.close()
        self.closeConnection()
        if has_result:
            return [dict(zip(col_names, record)) for record in records]

    def get_just_one(self, command, cls):
        """Метод возвращает ровно один экземпляр класса cls, если в базе найдено больше - вызывается искалючение,
        если не найдено совсем - возвращается none"""
        rows = self.executeCommand(command)
        if len(rows) > 2:
            raise Exception(f"Найдено {len(rows)} экземпляров cls, ожидался только один")
        if len(rows) == 0:
            return None
        return cls(rows[0])


class FiscalServiceHelper(PostgresHelper):
    """Класс для работы с базой СФ"""

    def set_sent_to_dbfiscal(self, document_id):
        command = f"UPDATE dbo.documents SET sent_to_fiscaldb = true where documentid <= {document_id} " \
                  "and sent_to_fiscaldb = false and documenttype in (1,8)"
        self.executeCommand(command, False)

    def copyFiscalItems(self):
        f = open('1.csv', 'w')
        self.openConnection()
        cur = self.connection.cursor()
        sql = f"SELECT t.ticketid, comp.inn, " \
              "t.ticketseries,  t.ticketnumber,  " \
              "t.dateins, t.datetrip, d.documentdate, now() as datecreate, " \
              "d.fiscalsign, t.paymenttype, 'NKZ', t.tax as taxid, t.vat as vatid, " \
              "d.fiscalnum,  s.fiscalstoragenum,  " \
              "t.price as ticketprice, s.sessionnum, d.num_in_session, " \
              "c.registrynumber as cashbox_reg_num, c.factorynumber as cashbox_factory_num, d.documentid," \
              " d.ms, t.datecreate as sf_datecreate, comp.companykpp, d.documenttype, null " \
              "FROM dbo.tickets t " \
              "JOIN dbo.documents d on (d.ticketid = t.ticketid) " \
              "JOIN dbo.sessions s on (s.sessionid = d.sessionid) " \
              "JOIN dbo.cashbox c on (c.cashboxid = s.cashboxid) " \
              "JOIN dbo.companies comp on (comp.id = c.companyid)" \
              "where d.sent_to_fiscaldb = false " \
              "and d.documenttype in (1,8) " \
              "order by d.documentid " \
              "limit 90000"
        cur.copy_expert(f"COPY ({sql}) TO STDOUT WITH CSV HEADER", f)
        self.closeConnection()
        f.close()

    def get_cashboxes(self):
        cashboxes = []
        command = "select * from dbo.cashbox"
        rows = self.executeCommand(command)
        for row in rows:
            cashboxes.append(Cashbox(row))
        return cashboxes

    def get_companies(self):
        answer = []
        command = "select * from dbo.companies where id > 0"
        records = self.executeCommand(command)
        for record in records:
            company = Company(record)
            answer.append(company)
        return answer

    def get_ofd_account(self, company):
        command = f"select login, password, o.id from dbo.ofd_accounts o " \
                  f"join dbo.companies on companies.ofd_account = o.id where " \
                  f"companies.id = {company.id}"
        records = self.executeCommand(command)
        if len(records) == 0:
            return None
        if len(records) > 1:
            raise Exception("Дубль")
        return records[0]


class FiscalDbHelper(PostgresHelper):

    def getMaxId(self, regionid):
        command = f"select max(documentid) from public.tickets_nfiscalticket where regionid = '{regionid}'"
        return self.executeCommand(command)

    def pastFiscalItems(self):
        f = open('1.csv', 'r')
        self.openConnection()
        cur = self.connection.cursor()
        cur.copy_expert(f"COPY public.tickets_nfiscalticket from STDIN WITH CSV HEADER", f)
        self.connection.commit()
        cur.close()
        self.closeConnection()
        f.close()

    def get_tickets_by_date_trip(self, company: Company, date_from, region, timezone):
        tickets = set()
        date_to = date_from + dt.timedelta(days=1)
        command = f"set timezone = '{timezone}'; select * from public.tickets_nfiscalticket " \
                  f"where regionid = '{region}' " \
                  f"and companyinn = '{company.inn}' and companykpp = '{company.kpp}' " \
                  f"and dateins >= '{date_from}' and dateins < '{date_to}' and ticketseries not like 'fake%'"
        rows = self.executeCommand(command)
        for row in rows:
            tickets.add(Ticket(row))
        return tickets

    def update_cashbox_reg_num(self, factory_number, registry_number):
        command = f"update public.tickets_cashbox set registry_number = '{registry_number}'" \
                  f" where factory_number = {factory_number}"
        self.executeCommand(command, False)

    def inser_cashbox(self, cashbox: Cashbox):
        command = "INSERT INTO public.tickets_cashbox(factory_number, registry_number)" \
                  f"VALUES({cashbox.factory_number}, '{cashbox.registry_number}')"
        self.executeCommand(command, False)

    def get_cashboxes(self):
        answer = []
        command = "SELECT * from public.tickets_cashbox"
        rows = self.executeCommand(command)
        for row in rows:
            cashbox = Cashbox()
            cashbox.id = row['id']
            cashbox.factory_number = row['factory_number']
            cashbox.registry_number = row['registry_number']
            answer.append(cashbox)
        return answer

    def update_documents_cashbox_id(self, old_id, new_id):
        command = f"update public.tickets_fiscaldocument set cashbox_id = {new_id} where cashbox_id = {old_id};"
        self.executeCommand(command, False)

    def remove_cashbox(self, other_cashbox):
        command = f"delete from public.tickets_cashbox where id = {other_cashbox.id}"
        self.executeCommand(command, False)

    def get_tickets_without_docs(self, idd):
        answer = []
        command = "SELECT id, company_id, price, vat_id," \
                  "date_trip, payment_type, ticket_number, ticket_series FROM public.tickets_fiscalticket TT " \
                  f"  WHERE id = {idd}"
        rows = self.executeCommand(command)
        for row in rows:
            answer.append(Ticket(row))
        return answer

    def get_document_for_ticket(self, ticket: Ticket):
        command = f"SELECT * from public.tickets_fiscaldocument where " \
                  f"ticket_id is null and date_fiscal > '{ticket.date_trip}' and company_id = {ticket.company_id} " \
                  f"and price = {ticket.price} and vat_id = {ticket.vat} " \
                  f"and type_id in (1,8,-1) and is_storned = FALSE limit 1"
        rows = self.executeCommand(command)
        if len(rows) == 0:
            return None
        return Document(rows[0])

    def set_ticket_for_document(self, ticket, document):
        command = f"update public.tickets_fiscaldocument set ticket_id = {ticket.id} where id = {document.id}"
        self.executeCommand(command, False)

    def insert_document(self, doc: Document, company_id, cashbox_id, tax_id, vat_id, ticket_id):
        command = "insert into tickets_fiscaldocument(date_create, fn_number, fiscal_number, fiscal_sign, " \
                  "session_num, num_in_session, date_fiscal, price, additional_prop, cashbox_id, company_id, tax_id, " \
                  "type_id, vat_id, payment_type, ms, is_storned, ticket_id) " \
                  f"VALUES(now(), {doc.fn_number}, {doc.fiscal_number}, {doc.fiscal_sign}, {doc.session_num}, " \
                  f"{doc.num_in_session}, '{doc.date_fiscal}', {doc.price}, '', " \
                  f"{cashbox_id}, " \
                  f"{company_id}, {tax_id}, {doc.type}, {vat_id}, {doc.payment_type}, -1, false, {ticket_id} ) RETURNING id;"
        answer = self.executeCommand(command)
        return answer[0]['id']

    def get_region_id_by_name(self, name):
        command = f"select * from public.tickets_region where name = '{name}' "
        region = self.get_just_one(command, Region)
        if region:
            return region.id

    def get_tax_id_by_name(self, name):
        command = f"select * from public.tickets_tax where name = '{name}' "
        tax = self.get_just_one(command, Tax)
        if tax:
            return tax.id

    def get_vat_id_by_name(self, name):
        command = f"select * from public.tickets_vat where name = '{name}' "
        vat = self.get_just_one(command, Vat)
        if vat:
            return vat.id

    def get_company_by_inn_kpp(self, inn, kpp):
        command = f"select * from public.tickets_company where inn = '{inn}' and kpp = '{kpp}' "
        return self.get_just_one(command, Company)

    def get_cashbox_by_factory_number(self, factory_number):
        command = f"select * from public.tickets_cashbox where factory_number = {factory_number} "
        return self.get_just_one(command, DbfCashbox)

    def existsDocument(self, document: Document):
        command = f"select 1 from public.tickets_fiscaldocument where fn_number = {document.fn_number} " \
                  f"and fiscal_number = {document.fiscal_number}"
        rows = self.executeCommand(command)
        return len(rows) > 0

    def delete_ticket(self, ticket):
        command = f"delete from public.tickets_fiscalticket where id = {ticket.id}"
        self.executeCommand(command, False)

    def existsCopy(self, ticket: Ticket):
        command = f"select 1 from public.tickets_fiscalticket where id != {ticket.id} " \
                  f"and ticket_series = '{ticket.ticket_series}' and ticket_number = '{ticket.ticket_number}'"
        rows = self.executeCommand(command)
        return len(rows) > 0

    def exists_document_by_ticket_id(self, ticket_id):
        command = f"select 1 from tickets_fiscaldocument where ticket_id = {ticket_id}"
        rows = self.executeCommand(command)
        return len(rows) > 0

    def get_ticket_by_fields(self, ticket_series, ticket_number, company_id):
        command = f"select * from tickets_fiscalticket where ticket_series = '{ticket_series}' " \
                  f"and ticket_number = '{ticket_number}' and company_id = {company_id} order by id limit 1"
        return self.get_just_one(command, Ticket)

    def unbound_documents_from_ticket(self, ticket):
        command = f"update tickets_fiscaldocument set ticket_id = null where ticket_id = {ticket.id}"
        self.executeCommand(command, False)


class OldFiscalDB(PostgresHelper):

    def __init__(self, dbname, user='postgres', password='qwerty', host='localhost', port='5432'):
        super().__init__(dbname, user=user, password=password, host=host, port=port)

    def get_document_by_ticket(self, ticket: Ticket):
        command = f"select * from public.tickets_nfiscalticket " \
                  f"where ticketseries = '{ticket.ticket_series}' and ticketnumber = '{ticket.ticket_number}' "
        rows = self.executeCommand(command)
        if len(rows) > 1:
            raise Exception("LE<KM")
        if len(rows) == 0:
            return None
        document = Document()
        record = rows[0]
        document.id = record['new_id']
        document.price = record['ticketprice']
        document.fiscal_sign = record['fiscalsign']
        document.fiscal_number = record['fiscalnum']
        document.fn_number = record['fiscalstoragenum']
        document.inn = record['companyinn']
        document.kpp = record['companykpp']
        document.payment_type = record['paymenttype']
        document.region = record['regionid']
        document.vat = record['vatid']
        document.tax = record['taxid']
        document.cashbox_factory_num = record['cashbox_factory_num']
        document.session_num = record['sessionnum']
        document.num_in_session = record['num_in_session']
        document.date_fiscal = record['datefiscal']
        document.type = record['documenttype']
        return document

    def get_documents(self, new_id):
        answer = []
        command = f"select * from public.tickets_nfiscalticket " \
                  f"where new_id <= {new_id}  and documenttype in (1,8) order by new_id desc limit 10000"
        rows = self.executeCommand(command)
        if len(rows) == 0:
            return None
        for row in rows:
            document = Document()
            record = row
            document.id = record['new_id']
            document.price = record['ticketprice']
            document.fiscal_sign = record['fiscalsign']
            document.fiscal_number = record['fiscalnum']
            document.fn_number = record['fiscalstoragenum']
            document.inn = record['companyinn']
            document.kpp = record['companykpp']
            document.payment_type = record['paymenttype']
            document.region = record['regionid']
            document.vat = record['vatid']
            document.tax = record['taxid']
            document.cashbox_factory_num = record['cashbox_factory_num']
            document.session_num = record['sessionnum']
            document.num_in_session = record['num_in_session']
            document.date_fiscal = record['datefiscal']
            document.type = record['documenttype']
            answer.append(document)
        return answer

    def exists_tickets(self, ticket: Ticket):
        command = f"select 1 from public.tickets_nfiscalticket where ticketseries = '{ticket.ticket_series}' and " \
                  f"ticketnumber = '{ticket.ticket_number}' "
        rows = self.executeCommand(command)
        return len(rows) > 0


class SettingsHelper(PostgresHelper):
    def __init__(self):
        super().__init__('settings')

    def getSettings(self):
        command = "SELECT * from dbo.settings"
        settings = None
        records = self.executeCommand(command)
        for record in records:
            settings = Settings(record)
        return settings

    def getErrorEmails(self):
        emails = []
        command = "Select email from dbo.recepients where errors"
        answer = self.executeCommand(command)
        for line in answer:
            emails.append(line['email'])
        return emails

    def updatePeriod(self, period):
        command = f"update dbo.settings set revise_period_end = '{period}'"
        self.executeCommand(command, has_result=False)

    def get_revise_emails(self):
        emails = []
        command = "Select email from dbo.recepients where revise"
        answer = self.executeCommand(command)
        for line in answer:
            emails.append(line['email'])
        return emails

    def set_revise_periods_null(self):
        command = "update dbo.settings set revise_date_from = null, revise_date_to = null"
        self.executeCommand(command, has_result=False)


class FinkHelper(PostgresHelper):
    def __init__(self):
        super().__init__('fink')

    def countWrongTickets(self):
        command = "select count(id) from dbo.wrongtickets"
        answer = self.executeCommand(command)
        return answer[0]['count']

    def get_divizions(self):
        command = "select divisionid from dbo.companies"
        answer = self.executeCommand(command)
        return [str(x['divisionid']) for x in answer]

    def get_divizions_by_company(self, inn, kpp):
        command = f"select divisionid from dbo.companies where companyinn = '{inn}' and companykpp = '{kpp}'"
        answer = self.executeCommand(command)
        if len(answer) == 0:
            return None
        return [str(x['divisionid']) for x in answer]

    def get_asuop_settings(self):
        settings = []
        command = 'select * from dbo.sources where id = 3'
        answer = self.executeCommand(command)
        for row in answer:
            settings.append(SourceSettings(row))
        return settings

    def get_companies(self):
        companies = []
        command = 'select * from dbo.companies where status = 1'
        answer = self.executeCommand(command)
        for row in answer:
            company = Company()
            company.init_from_fink(row)
            companies.append(company)
        return companies

    def get_routes(self):
        routes = []
        command = "select * from dbo.routes"
        answer = self.executeCommand(command)
        for row in answer:
            route = FinkRoute(row)
            routes.append(route)
        return routes

    def get_last_query_time(self):
        command = "set time zone 'utc'; select dateend from dbo.fiscallog order by fiscallogid desc limit 1"
        rows = self.executeCommand(command)
        if len(rows) == 0:
            return None
        return rows[0]['dateend']


class DbHelper(PostgresHelper):
    def __init__(self):
        super().__init__('fiscaldb', host='10.2.50.17')

    def document_exists(self, fn_num, session_num, num_in_session):
        command = f"select count(1) from public.tickets_nfiscalticket where fiscalstoragenum = {fn_num} and " \
                  f"sessionnum = {session_num} and num_in_session = {num_in_session}"
        answer = self.executeCommand(command)
        return answer[0]['count'] == 1

    def getSumFiscalised(self, date_from: dt.date, regionid, paymenttype, company, timezone):
        date_to = date_from + dt.timedelta(days=1)
        command = f"set timezone = '{timezone}'; select sum(ticketprice) from public.tickets_nfiscalticket " \
                  f"where regionid = '{regionid}' " \
                  f"and datefiscal >= '{date_from}' and datefiscal < '{date_to}' and paymenttype = {paymenttype} " \
                  f"and companyinn = '{company.inn}' and companykpp = '{company.kpp}'"
        answer = self.executeCommand(command)[0]['sum']
        if answer is None:
            return 0
        return answer

    def getSum(self, dt_from: dt.datetime, dt_to: dt.datetime, regionid, company, paymenttype):
        command = f"set timezone = 'utc'; select sum(ticketprice) from public.tickets_nfiscalticket where" \
                  f" regionid = '{regionid}' " \
                  f"and dateins >= '{dt_from}' and dateins < '{dt_to}' and paymenttype = {paymenttype} " \
                  f"and companyinn = '{company.inn}' and companykpp = '{company.kpp}' "
        answer = self.executeCommand(command)[0]['sum']
        if answer is None:
            return 0
        return answer

    def updateDocumentDate(self, fiscalnum, fn_number, documentdate):
        command = f"set timezone = 'utc';  update public.tickets_nfiscalticket" \
                  f" set datefiscal = '{documentdate}' where regionid = 'NKZ' " \
                  f"and fiscalnum = {fiscalnum} and fiscalstoragenum = {fn_number} "
        self.executeCommand(command, False)


    def get_tickets_by_date_ins(self, company: Company, date_from, region, timezone):
        tickets = set()
        date_to = date_from + dt.timedelta(days=1)
        command = f"set timezone = '{timezone}'; select * from public.tickets_nfiscalticket " \
                  f"where regionid = '{region}' " \
                  f"and companyinn = '{company.inn}' and companykpp = '{company.kpp}' " \
                  f"and dateins >= '{date_from}' and dateins < '{date_to}' and ticketseries not like 'fake%'"
        rows = self.executeCommand(command)
        for row in rows:
            tickets.add(Ticket(row))
        return tickets

    def get_ticket(self, inn, kpp, ticket_series, ticket_number, date_trip):
        command = "set timezone = 'utc'; select * from public.tickets_nfiscalticket " \
                  f"where companyinn = '{inn}' and companykpp = '{kpp}' and ticketseries = '{ticket_series}' and " \
                  f"ticketnumber = '{ticket_number}' and datetrip = '{date_trip}' "
        rows = self.executeCommand(command)
        if len(rows) > 1:
            raise Exception("Дублирующийся билет")
        if len(rows) == 1:
            return Ticket(rows[0])

    def updateTicketDates(self, inn, kpp, ticket_series, ticket_number, date_trip, date_ins):
        command = f"set timezone = 'utc';  update public.tickets_nfiscalticket" \
                  f" set datetrip = '{date_trip}', dateins = '{date_ins}' where regionid = 'SPB' " \
                  f"and companyinn = '{inn}' and companykpp = '{kpp}' and ticketseries = '{ticket_series}' " \
                  f"and ticketnumber = '{ticket_number}' "
        self.executeCommand(command, False)

    def insert_into_wrong_tickets(self, ticket: Ticket):
        command = f"set timezone= 'utc'; insert into public.spb_wrong_tickets values('{ticket.inn}', '{ticket.kpp}', " \
                  f"'{ticket.ticket_series}', '{ticket.ticket_number}')"
        self.executeCommand(command, False)

    def update_series_number_fake(self, ticket, counter):
        command = f"set timezone = 'utc';  update public.tickets_nfiscalticket" \
                  f" set ticketseries = 'fake', ticketnumber = '{counter}' where regionid = 'SPB' " \
                  f"and companyinn = '{ticket.inn}' and companykpp = '{ticket.kpp}' " \
                  f"and ticketseries = '{ticket.ticket_series}' " \
                  f"and ticketnumber = '{ticket.ticket_number}' "
        self.executeCommand(command, False)
        print(ticket, counter)

    def get_fake_ticket(self, ticket):
        command = "set timezone = 'utc'; select * from public.tickets_nfiscalticket where ticketseries = 'fake' and " \
                  f"companyinn = '{ticket.inn}' and companykpp = '{ticket.kpp}' and datetrip = '{ticket.date_trip}' " \
                  f"limit 1"
        rows = self.executeCommand(command)
        if len(rows) == 1:
            return Ticket(rows[0])

    def update_fake_ticket(self, fake_ticket, ticket):
        command = f"set timezone = 'utc';  update public.tickets_nfiscalticket" \
                  f" set ticketseries = '{ticket.ticket_series}', ticketnumber = '{ticket.ticket_number}', " \
                  f"dateins = '{ticket.date_ins}' where regionid = 'SPB' " \
                  f"and companyinn = '{ticket.inn}' and companykpp = '{ticket.kpp}' " \
                  f"and ticketseries = 'fake' " \
                  f"and ticketnumber = '{fake_ticket.ticket_number}' "
        self.executeCommand(command, False)

    def get_ticket_by_fiscal_data(self, fn_number, fiscal_number):
        command = f"select * from public.tickets_nfiscalticket " \
                  f"where fiscalstoragenum = {fn_number} and fiscalnum = {fiscal_number} "
        rows = self.executeCommand(command)
        if len(rows) > 1:
            raise Exception("Неверное количество документов получено по фискальным признакам")
        if len(rows) == 1:
            return Ticket(rows[0])

    def update_fiscal_date(self, fn_number, fiscal_number, new_fiscal_date):
        command = f"update public.tickets_nfiscalticket set datefiscal = '{new_fiscal_date}' " \
                  f"where fiscalstoragenum = {fn_number} and fiscalnum = {fiscal_number} "
        self.executeCommand(command, False)

    def set_ticket_fake(self, ticket):
        command = f"update public.tickets_nfiscalticket set ticketseries = '{'fake' + ticket.ticket_series}' where new_id = {ticket.id} "
        self.executeCommand(command, False)

    def get_tickets_by_date_trip(self, company, date, region, timezone):
        pass
