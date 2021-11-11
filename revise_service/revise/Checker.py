import datetime
#
#     def make_excel(self):
#         name = str(self.date) + '.xlsx'
#         workbook = xlsxwriter.Workbook(name, {'remove_timezone': True})
#         header_format = workbook.add_format({'bold': True})
#         if len(self.missed_tickets):
#             worksheet = workbook.add_worksheet("Недостающие билеты")
#
#             worksheet.write_row(0, 0, ["Серия Билета", "Номер билета", "Дата поездки", "Дата вставки", "Номинал",
#                                        "ИНН", "КПП", "Ссылка на запись в источнике"], header_format)
#
#             i = 1
#             for ticket in self.missed_tickets:
#                 worksheet.write_row(i, 0,
#                                     [ticket.ticket_series, ticket.ticket_number,
#                                      str(ticket.date_trip), str(ticket.date_ins), ticket.price, ticket.inn,
#                                      ticket.kpp, str(ticket.id)])
#                 i += 1
#
#         if len(self.additional_tickets):
#             worksheet = workbook.add_worksheet("Лишние билеты")
#             worksheet.write_row(0, 0, ["Серия Билета", "Номер билета", "Дата поездки", "Дата вставки", "Номинал",
#                                        "ИНН", "КПП", "Ссылка на запись"], header_format)
#
#             i = 1
#             for ticket in self.additional_tickets:
#                 worksheet.write_row(i, 0,
#                                     [ticket.ticket_series, ticket.ticket_number, str(ticket.date_trip),
#                                      str(ticket.date_ins), ticket.price, ticket.inn, ticket.kpp,
#                                      ticket.id])
#                 i += 1
#
#         if len(self.missed_documents):
#             worksheet = workbook.add_worksheet("Недостающие документы")
#             worksheet.write_row(0, 0, ["Номер фискального накопителя", "Номер Документа", "ФПД", "Дата фискализации",
#                                        "Номинал", "Ставка", "Тип документа"], header_format)
#
#             i = 1
#             for document in self.missed_documents:
#                 worksheet.write_row(i, 0,
#                                     [str(document.fn_number), document.fiscal_number, str(document.fiscal_sign),
#                                      str(document.date_fiscal),
#                                      document.price,
#                                      document.vat,
#                                      document.type])
#                 i += 1
#
#         if len(self.additional_documents):
#             worksheet = workbook.add_worksheet("Лишние документы")
#             worksheet.write_row(0, 0, ["Номер фискального накопителя", "Номер Документа", "ФПД", "Дата фискализации",
#                                        "Номинал", "Ставка", "Тип документа"], header_format)
#
#             i = 1
#             for document in self.additional_documents:
#                 worksheet.write_row(i, 0,
#                                     [str(document.fn_number), document.fiscal_number, str(document.fiscal_sign),
#                                      str(document.date_fiscal),
#                                      document.price,
#                                      document.vat,
#                                      document.type])
#                 i += 1
#         workbook.close()
#         self.filename = name
#

from core.entities.Enums import PaymentType
from core.sources.Source_Helper import sources_cache_tickets
from core.asyncdb.PostgresHelper import PostgresHelperDbf
from core.entities.entities import Company
from core.entities.entity_schemas import CompanySchema

from core.redis_api.RedisApi import RedisApi
from revise.OFDHelper import OFDHelper

from core.utils import change_timezone
from core.webax_api.WebaxHelper import WebaxHelper


class Revise:
    def __init__(self,
                 date_from: datetime.date,
                 date_to: datetime.date,
                 need_cash: bool,
                 need_non_cash: bool,
                 need_tickets: bool,
                 need_documents: bool,
                 companies: list = None,
                 email: str = None):
        self.date_from = date_from
        self.date_to = date_to + datetime.timedelta(hours=23, minutes=59, seconds=59)
        self.need_cash = need_cash
        self.need_non_cash = need_non_cash
        self.need_tickets = need_tickets
        self.need_documents = need_documents
        self.companies_party_id: list = companies
        self.email = email
        self.companies = set()
        self.dbf_tickets = set()
        self.dbf_documents = set()
        self.asuop_tickets = set()
        self.ofd_documents: set = set()
        self.missed_tickets = set()
        self.additional_tickets = set()
        self.missed_documents = set()
        self.additional_documents = set()
        self.redis = RedisApi()
        self.postgres = PostgresHelperDbf()
        self.webax = WebaxHelper()
        self.has_error = False

    async def run(self):
        await self.cache()
        dt = self.date_from
        while dt <= self.date_to:
            for company in self.companies:
                await self.revise_company_on_date(company, dt)
            dt += datetime.timedelta(days=1)

    async def revise_company_on_date(self, company: Company, on_date: datetime.date):
        answer = ''
        has_error = False
        dt_start = datetime.datetime(on_date.year, on_date.month, on_date.day)
        dt_end = dt_start + datetime.timedelta(hours=24)
        dt_start = change_timezone(dt_start, 'UTC', 'UTC')
        dt_end = change_timezone(dt_end, 'UTC', 'UTC')
        asuop_tickets = set(x for x in self.asuop_tickets if
                            x.company_id == company.id and dt_start <= x.date_ins < dt_end)  # TODO, неоправданно долго, мб заменить на filter()
        dbf_tickets = set(
            x for x in self.dbf_tickets if x.company_id == company.id and dt_start <= x.date_ins < dt_end)
        ofd_documents = set(
            x for x in self.ofd_documents if x.company_id == company.id and dt_start <= x.date_fiscal < dt_end)
        dbf_documents = set(x for x in self.dbf_documents if x.company_id == company.id
                            and dt_start <= x.date_fiscal < dt_end)

        amount_tickets_asuop_cash = int(sum(x.price for x in asuop_tickets if x.payment_type == PaymentType.CASH) / 100)
        amount_tickets_asuop_cashless = int(
            sum(x.price for x in asuop_tickets if x.payment_type == PaymentType.NON_CASH) / 100)
        amount_tickets_db_cash = int(sum(x.price for x in dbf_tickets if x.payment_type == PaymentType.CASH) / 100)
        amount_tickets_db_cashless = int(sum(x.price for x in dbf_tickets if
                                             x.payment_type == PaymentType.NON_CASH) / 100)
        amount_documents_ofd_cash = int(sum(x.price for x in ofd_documents if x.payment_type == PaymentType.CASH) / 100)
        amount_documents_ofd_cashless = int(sum(x.price for x in ofd_documents if
                                                x.payment_type == PaymentType.NON_CASH) / 100)
        amount_documents_db_cash = int(sum(x.price for x in dbf_documents if x.payment_type == PaymentType.CASH) / 100)
        amount_documents_db_cashless = int(sum(x.price for x in dbf_documents if
                                               x.payment_type == PaymentType.NON_CASH) / 100)

        if amount_tickets_asuop_cash + amount_tickets_asuop_cashless != \
                amount_tickets_db_cash + amount_tickets_db_cashless:
            answer += 'Обнаружены расхождения по сумме билетов\n'
            has_error = True

        if amount_documents_ofd_cash + amount_documents_ofd_cashless != \
                amount_documents_db_cash + amount_documents_db_cashless:
            answer += 'Обнаружены расхождения по сумме документов\n'
            has_error = True

        missed_tickets = asuop_tickets.difference(dbf_tickets)
        additional_tickets = dbf_tickets.difference(asuop_tickets)
        missed_documents = ofd_documents.difference(dbf_documents)
        additional_documents = dbf_documents.difference(ofd_documents)




        if len(missed_tickets) + len(additional_tickets) > 0:
            answer += 'Обнаружены расхождения по билетам\n'
            has_error = True

        if len(missed_documents) + len(additional_documents) > 0:
            answer += 'Обнаружены расхождения по документам\n'
            has_error = True
            ofd_helper = OFDHelper(company.ofd_login, company.ofd_password)
            for doc in missed_documents:
                if doc.fiscal_sign == -1:
                    full_data = await ofd_helper.get_ful_data(company.inn, doc.cashbox_reg_num, doc.id)
                    doc.tax = full_data.tax
                    doc.additional_prop = full_data.additional_prop
                    doc.fiscal_sign = int(full_data.fiscal_sign)

        await self.webax.update_revise_data(company, additional_tickets, missed_tickets,
                                            additional_documents, missed_documents, self.has_error or has_error,
                                            on_date,
                                            amount_tickets_db_cash, amount_tickets_db_cashless,
                                            amount_tickets_asuop_cash, amount_tickets_asuop_cashless,
                                            amount_documents_db_cash, amount_documents_db_cashless,
                                            amount_documents_ofd_cash, amount_documents_ofd_cashless,
                                            company.answer + answer)

    async def cache_ofd_document(self, date_from, date_to, companies):
        for company in companies:
            ofd_documents = None
            if company.ofd_login and company.ofd_password:
                ofd_helper = OFDHelper(company.ofd_login, company.ofd_password)
                if ofd_helper.token:
                    cashboxes = await self.redis.get_cashboxes(company.id)
                    ofd_documents = await ofd_helper.get_documents(company, date_from, date_to, cashboxes)
                    if ofd_documents is not None:
                        self.ofd_documents = self.ofd_documents.union(ofd_documents)
                if ofd_helper.token is None or ofd_documents is None:
                    company.answer += 'Ошибка при попытке получить доступ в ОФД \n'
                    self.has_error = True
            else:
                company.answer += 'Нет учётных данных для ОФД \n'

    async def cache(self):
        """Если сверка запущена сразу по всему региону или за несколько дней, то чтобы не лазать в базу несколько раз -
        кэшируем записи сразу"""

        for company in self.companies:
            company.answer = ''
        date_time_from = datetime.datetime(self.date_from.year, self.date_from.month, self.date_from.day)
        date_time_to = datetime.datetime(self.date_to.year, self.date_to.month, self.date_to.day) \
                       + datetime.timedelta(hours=23, minutes=59, seconds=59)

        if self.need_tickets:
            self.dbf_tickets = await self.postgres.get_tickets_by_date_ins(date_time_from, date_time_to,
                                                                           self.companies)
            self.asuop_tickets = await sources_cache_tickets(date_time_from, date_time_to, self.companies)
        if self.need_documents:
            self.dbf_documents = await self.postgres.get_documents_by_date_fiscal(date_time_from, date_time_to,
                                                                                  self.companies)
            await self.cache_ofd_document(date_time_from, date_time_to, self.companies)

    async def init(self):
        for party_id in self.companies_party_id:
            company = await self.redis.get_entity(party_id, CompanySchema())
            if not company:
                return f"Компания с party_id {party_id} не существует"
            self.companies.add(company)



