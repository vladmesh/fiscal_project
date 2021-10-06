from datetime import datetime

import mysql.connector

from core.Ticket import Ticket
from core.utils import strip


class MySqlHelper:
    def __init__(self, host, database, login, password):
        self.host = host
        self.database = database
        self.login = login
        self.password = password
        self.connection = None
        self.cursor = None

    def open_connection(self):
        self.connection = mysql.connector.connect(user=self.login, password=self.password, host=self.host,
                                                  database=self.database)
        self.cursor = self.connection.cursor()

    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    def execute_query(self, query, has_result=True):
        answer = []
        self.open_connection()
        self.cursor.execute(query)

        if has_result:
            rows = self.cursor.fetchall()
            for row in rows:
                record_dict = {}  # каждой записи сопоставляем словарь, типа {Имя колонки : значение}
                for i in range(len(self.cursor.description)):
                    record_dict[self.cursor.description[i][0]] = strip(row[i])
                answer.append(record_dict)
        self.connection.commit()
        self.close_connection()
        if has_result:
            return answer


