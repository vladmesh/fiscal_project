import asyncio
import datetime

# class CompanyChecker:
#     def __init__(self, company: Company, settings, date):
#         self.company = company
#         self.has_error = False
#         self.has_warning = False
#         self.additional_tickets = set()
#         self.additional_documents = set()
#         self.missed_tickets = set()
#         self.missed_documents = set()
#         self.fiscalHelper = FiscalServiceHelper()
#         self.settings = settings
#         self.ofdHelper = OFDHelper(self.settings.ofd_login, self.settings.ofd_password)
#         self.region = self.settings.server_name
#         self.message = ''
#         self.date = date
#         self.amount_tickets_db_cash = 0
#         self.amount_tickets_db_cashless = 0
#         self.amount_documents_db_cash = 0
#         self.amount_documents_db_cashless = 0
#         self.amount_tickets_asuop_cash = 0
#         self.amount_tickets_asuop_cashless = 0
#         self.amount_documents_ofd_cash = 0
#         self.amount_documents_ofd_cashless = 0
#         self.answer = ''
#         self.has_ofd_access = None
#
#     def check_fiscal_sum(self, cashboxes, dbf_documents: set):
#         self.message += '<pre>\tПроверка сумм по дате фискализации<br></pre>'
#         ofd_account = self.fiscalHelper.get_ofd_account(self.company)
#
#         if ofd_account is None:
#             self.message += '<pre>\t\t<font style="color:#E77426">Нет учётных данных для доступа в ОФД' \
#                             '</font></pre><br>'
#             self.has_ofd_access = False
#             self.answer += "Нет учётных данных для ОФД. "
#             return
#         self.has_ofd_access = True
#         self.ofdHelper = OFDHelper(ofd_account['login'], ofd_account['password'])
#         if self.ofdHelper.token is None:
#             self.message += '<pre>\t\t<font style="color:red">Не удалось получить список документов из ОФД, ' \
#                             'нет доступа' \
#                             '</font></pre><br>'
#             self.answer = "Нет доступа к API ОФД. "
#             self.has_error = True
#             return
#
#         flag = self.company.id == 3 and self.date == datetime.date(2021, 8, 4) and self.region == 'SCH'
#         ofd_documents = self.ofdHelper.get_documents(self.company, self.date, self.date + datetime.timedelta(days=1),
#                                                      cashboxes, self.settings.timezone,
#                                                      not flag)
#         if ofd_documents is None:
#             self.message += '<pre>\t\t<font style="color:red">Не удалось получить список документов из ОФД, ' \
#                             'ошибка при обработке ответа' \
#                             '</font></pre><br>'
#             self.has_error = True
#             self.answer += "Некорректный ответ от ОФД. "
#             return
#
#         self.amount_documents_ofd_cash = int(sum(x.price for x in ofd_documents if x.payment_type == 1) / 100)
#         self.amount_documents_ofd_cashless = int(sum(x.price for x in ofd_documents if x.payment_type == 2) / 100)
#         self.amount_documents_db_cash = int(sum(x.price for x in dbf_documents if x.payment_type == 1) / 100)
#         self.amount_documents_db_cashless = int(sum(x.price for x in dbf_documents if x.payment_type == 2) / 100)
#         self.message += f"<pre>\t\tСумма фискализированных наличных в ОФД - {self.amount_documents_ofd_cash}</pre><br>"
#         self.message += f"<pre>\t\tСумма наличных по дате фискализации в dbfiscal - " \
#                         f"{self.amount_documents_db_cash}</pre><br>"
#         self.message += '<br>'
#         self.message += f"<pre>\t\tСумма фискализации по безналу в ОФД - {self.amount_documents_ofd_cashless}</pre><br>"
#         self.message += f"<pre>\t\tСумма безнала по дате фискализации в dbfiscal - " \
#                         f"{self.amount_documents_db_cashless}</pre><br>"
#         self.missed_documents = ofd_documents.difference(dbf_documents)
#         self.additional_documents = dbf_documents.difference(ofd_documents)
#         if len(self.missed_documents) > 0 or len(self.additional_documents) > 0:
#             for doc in self.missed_documents:
#                 if doc.fiscal_sign == -1:
#                     ful_data = self.ofdHelper.get_ful_data(doc.inn, doc.cashbox_reg_num, doc.id)
#                     doc.tax = ful_data.tax
#                     doc.additional_prop = ful_data.additional_prop
#                     doc.fiscal_sign = ful_data.fiscal_sign
#             self.message += '<pre>\t\t<font style="color:red"> Внимание, обнаружены расхождения по документам, ' \
#                             'подробности в приложенном файле <br></pre> </font> '
#             self.answer += "Расхождения по документам. "
#             self.has_error = True
#         if self.amount_documents_ofd_cash != self.amount_documents_db_cash or \
#                 self.amount_documents_ofd_cashless != self.amount_documents_db_cashless:
#             self.answer += "Расхождения по сумме документов. "
#             self.message += '<pre>\t\t<font style="color:red"> Внимание, обнаружены расхождения по суммам <br></pre> ' \
#                             '</font> '
#             self.has_error = True
#         self.message += '<br>'
#
#     def check_sum(self, asuop_tickets: set, dbf_tickets):
#         self.message += '<pre>Проверка сумм по дате вставки</pre><br>'
#         self.amount_tickets_asuop_cash = int(sum(x.price for x in asuop_tickets if x.payment_type == 1) / 100)
#         self.amount_tickets_asuop_cashless = int(sum(x.price for x in asuop_tickets if x.payment_type == 2) / 100)
#         self.amount_tickets_db_cash = int(sum(x.price for x in dbf_tickets if x.payment_type == 1) / 100)
#         self.amount_tickets_db_cashless = int(sum(x.price for x in dbf_tickets if x.payment_type == 2) / 100)
#         self.message += f"<pre>\t\tСумма наличных в АСУОП - {self.amount_tickets_asuop_cash}</pre><br>"
#         self.message += f"<pre>\t\tСумма наличных по дате вставки в dbfiscal - {self.amount_tickets_db_cash}</pre><br>"
#         self.message += '<br>'
#         self.message += f"<pre>\t\tСумма безнала в АСУОП - {self.amount_tickets_asuop_cashless}</pre><br>"
#         self.message += f"<pre>\t\tСумма безнала по дате вставки в dbfiscal - " \
#                         f"{self.amount_tickets_db_cashless}</pre><br>"
#         self.missed_tickets = asuop_tickets.difference(dbf_tickets)
#         self.additional_tickets = dbf_tickets.difference(asuop_tickets)
#         if len(self.missed_tickets) > 0 or len(self.additional_tickets) > 0:
#             self.message += '<pre>\t\t<font style="color:red"> Внимание, обнаружены расхождения по билетам, ' \
#                             'подробности в прилагаемом файле </pre><br> ' \
#                             '</font> '
#             self.has_error = True
#             self.answer += "Расхождения по билетам. "
#         if self.amount_tickets_asuop_cash != self.amount_tickets_db_cash or \
#                 self.amount_tickets_asuop_cashless != self.amount_tickets_db_cashless:
#             self.message += '<pre>\t<font style="color:red"> Внимание, обнаружены расхождения по сумме</pre><br> ' \
#                             '</font> '
#             self.has_error = True
#             self.answer += "Расхождения по сумме билетов. "
#         self.message += '<br>'
#
#     def check(self, asuop_tickets: set, dbf_documents: set, dbf_tickets: set, cashboxes: list):
#         try:
#             self.message += f'Сверка по компании {self.company.name}<br>'
#             self.message += '-' * 100 + '<br>'
#             self.check_sum(asuop_tickets, dbf_tickets)
#             self.check_fiscal_sum(cashboxes, dbf_documents)
#             self.message += '-' * 100 + '<br><br>'
#         except Exception as e:
#             self.has_error = True
#             self.answer = str(e)
#         self.send_json()
#
#     def send_json(self):
#         wh = WebaxHelper()
#         wh.update_revise_data(self.settings.server_name, self.company, self.additional_tickets, self.missed_tickets,
#                               self.additional_documents, self.missed_documents, self.has_error,
#                               self.has_warning, self.date, self.amount_tickets_db_cash, self.amount_tickets_db_cashless,
#                               self.amount_tickets_asuop_cash, self.amount_tickets_asuop_cashless,
#                               self.amount_documents_db_cash, self.amount_documents_db_cashless,
#                               self.amount_documents_ofd_cash, self.amount_documents_ofd_cashless, self.answer,
#                               self.has_ofd_access)
#
#
# class Checker:
#     def __init__(self, on_date):
#         self.date = on_date
#         self.settingsHelper = SettingsHelper()
#         self.settings = self.settingsHelper.getSettings()
#         self.fiscalHelper = FiscalServiceHelper()
#         self.finkHelper = FinkHelper()
#         self.hasError = False
#         self.message = ""
#         self.region = self.settings.server_name
#         self.cashboxes = self.fiscalHelper.get_cashboxes()
#         self.dbHelper = DbHelper()
#         self.asuop_tickets = set()
#         self.dbf_documents = set()
#         self.dbf_tickets = set()
#         self.missed_tickets = set()
#         self.additional_tickets = set()
#         self.missed_documents = set()
#         self.additional_documents = set()
#         self.filename = None
#         self.amount_tickets_db_cash = 0
#         self.amount_tickets_db_cashless = 0
#         self.amount_documents_db_cash = 0
#         self.amount_documents_db_cashless = 0
#         self.amount_tickets_asuop_cash = 0
#         self.amount_tickets_asuop_cashless = 0
#         self.amount_documents_ofd_cash = 0
#         self.amount_documents_ofd_cashless = 0
#
#     def dt_to_local_dt(self, dt: datetime.datetime):
#         from_zone = tz.gettz('UTC')
#         to_zone = tz.gettz(self.settings.timezone)
#         utc = dt.replace(tzinfo=from_zone)
#         local = utc.astimezone(to_zone)
#         return local
#
#     def send_mail(self):
#         emails = self.settingsHelper.get_revise_emails()
#         if self.hasError:
#             emails = self.settingsHelper.getErrorEmails()
#         header = f"{self.region}. Сверка за {self.date}"
#         if self.hasError:
#             header = f"{self.region} Ошибка. " + header
#         MailSender.send(self.message, header, emails, True, self.filename)
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
#     def cash_asuop_tickets(self, date_from, date_to):
#         date_from = change_timezone(date_from, self.settings.timezone, 'utc')
#         date_to = change_timezone(date_to, self.settings.timezone, 'utc')
#         asuop_settings = self.finkHelper.get_asuop_settings()
#         for sett in asuop_settings:
#             asuop_helper = construct(sett)
#             self.asuop_tickets = self.asuop_tickets.union(asuop_helper.get_tickets_on_date(date_from, date_to,
#                                                                                            self.settings.timezone))
#
#     def cash_dbf_documents(self, date_from, date_to):
#         date_from = change_timezone(date_from, self.settings.timezone, 'utc')
#         date_to = change_timezone(date_to, self.settings.timezone, 'utc')
#         region = self.dbHelper.get_region_id_by_name(self.region)
#         self.dbf_documents = self.dbHelper.get_documents_by_date_fiscal(date_from, date_to, region,
#                                                                         self.settings.timezone)
#
#     def cash_dbf_tickets(self, date_from, date_to):
#         date_from = change_timezone(date_from, self.settings.timezone, 'utc')
#         date_to = change_timezone(date_to, self.settings.timezone, 'utc')
#         region = self.dbHelper.get_region_id_by_name(self.region)
#         self.dbf_tickets = self.dbHelper.get_tickets_by_date_ins(date_from, date_to, region, self.settings.timezone)
#
#     def cash_tickets(self):
#         date_from = datetime.datetime(self.date.year, self.date.month, self.date.day)  # начало и конец дня считаются
#         # по времени региона, потому что так возвращает протокол ОФД и проще было подстроить всё под него
#         date_to = date_from + datetime.timedelta(days=1)
#         self.cash_asuop_tickets(date_from, date_to)
#         self.cash_dbf_documents(date_from, date_to)
#         self.cash_dbf_tickets(date_from, date_to)
#
#     def check(self):
#         companies = self.fiscalHelper.get_companies()
#         for company in companies:
#             self.check_company(company)
#         if len(self.additional_documents) + len(self.additional_tickets) + len(self.missed_documents) \
#                 + len(self.missed_tickets) > 0:
#             self.make_excel()
#
#     def check_company(self, company: Company):
#         asuop_tickets = set(x for x in self.asuop_tickets if x.inn == company.inn and x.kpp == company.kpp)
#         cashboxes = [x for x in self.cashboxes if x.company_id == company.id]
#         dbf_documents = set(x for x in self.dbf_documents if x.inn == company.inn and x.kpp == company.kpp)
#         dbf_tickets = set(x for x in self.dbf_tickets if x.inn == company.inn and x.kpp == company.kpp)
#         company_checker = CompanyChecker(company, self.settings, self.date)
#         company_checker.check(asuop_tickets, dbf_documents, dbf_tickets, cashboxes)
#         self.merge_data(company_checker)
#
#     def merge_data(self, company_checker: CompanyChecker):
#         self.message += company_checker.message
#         self.amount_tickets_db_cash += company_checker.amount_tickets_db_cash
#         self.amount_tickets_db_cashless += company_checker.amount_tickets_db_cashless
#         self.amount_documents_db_cash += company_checker.amount_documents_db_cash
#         self.amount_documents_db_cashless += company_checker.amount_documents_db_cashless
#         self.amount_tickets_asuop_cash += company_checker.amount_tickets_asuop_cash
#         self.amount_tickets_asuop_cashless += company_checker.amount_tickets_asuop_cashless
#         self.amount_documents_ofd_cash += company_checker.amount_documents_ofd_cash
#         self.amount_documents_ofd_cashless += company_checker.amount_documents_ofd_cashless
#         if company_checker.has_error:
#             self.hasError = True
#             self.missed_tickets = self.missed_tickets.union(company_checker.missed_tickets)
#             self.missed_documents = self.missed_documents.union(company_checker.missed_documents)
#             self.additional_tickets = self.additional_tickets.union(company_checker.additional_tickets)
#             self.additional_documents = self.additional_documents.union(company_checker.additional_documents)
from core.ASUOP_Helper import sources_cache_tickets
from core.asyncdb.PostgresHelper import PostgresHelperDbf
from core.entities.entities import Company
from core.entities.entity_schemas import CompanySchema

from core.redis_api.RedisApi import RedisApi
from core.utils import change_timezone


class Revise:
    def __init__(self,
                 revise_id: str,
                 date_from: datetime.date,
                 date_to: datetime.date,
                 need_cash: bool,
                 need_non_cash: bool,
                 need_tickets: bool,
                 need_documents: bool,
                 companies: list = None,
                 email: str = None):
        self.revise_id = revise_id
        self.date_from = date_from
        self.date_to = date_to
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
        self.ofd_documents = set()
        self.missed_tickets = set()
        self.additional_tickets = set()
        self.missed_documents = set()
        self.additional_documents = set()
        self.redis = RedisApi()
        self.postgres = PostgresHelperDbf()

    async def run(self):
        await self.cache()
        dt = self.date_from
        while dt <= self.date_to:
            for company in self.companies:
                await self.revise_company_on_date(company, dt)
            dt += datetime.timedelta(days=1)

    async def revise_company_on_date(self, company: Company, on_date: datetime.date):
        pass

    async def cache(self):
        """Если сверка запущена сразу по всему региону или за несколько дней, то чтобы не лазать в базу несколько раз -
        кэшируем записи сразу"""

        dbf_company_ids = []
        for company in self.companies:
            company_id = await self.postgres.get_company_id_by_inn_kpp(company.inn, company.kpp)
            dbf_company_ids.append(str(company_id))
        date_time_from = datetime.datetime(self.date_from.year, self.date_from.month, self.date_from.day)
        date_time_to = datetime.datetime(self.date_to.year, self.date_to.month, self.date_to.day)
        company_ids_str = f"({', '.join(dbf_company_ids)})"
        if self.need_tickets:
            self.dbf_tickets = await self.postgres.get_tickets_by_date_ins(date_time_from, date_time_to, company_ids_str)
            # TODO  Из источников тоже бы с учётом компаний тянуть
            self.asuop_tickets = await sources_cache_tickets(date_time_from, date_time_to)
            self.missed_tickets = self.asuop_tickets.difference(self.dbf_tickets)
            self.additional_tickets = self.dbf_tickets.difference(self.asuop_tickets)
            if len(self.missed_tickets) + len(self.additional_tickets) > 0:
                print("Bug")
        if self.need_documents:
            self.dbf_documents = await self.postgres.get_documents_by_date_fiscal(date_time_to, date_time_to,
                                                                                  company_ids_str)
            self.ofd_documents = set()

    async def init(self):
        for party_id in self.companies_party_id:
            company = await self.redis.get_entity(party_id, CompanySchema())
            if not company:
                return f"Компания с party_id {party_id} не существует"
            self.companies.add(company)
