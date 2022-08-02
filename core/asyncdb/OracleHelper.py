import cx_Oracle

# TODO Тут бы тоже нужно какую-то асинхронную либу, но у меня не получилось подключиться ни через cx_Oracle_async,
# TODO ни через aioodbc

class OracleHelper:
    def __init__(self, conn_string):
        self.connString = conn_string
        self.conn = None
        self.cursor = None

    def open(self):
        try:
            self.conn = cx_Oracle.connect(self.connString)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)

    def close(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, command, has_result=True):
        print("start blocking func")
        records = []
        col_names = []
        self.open()
        self.cursor.execute(command)
        if has_result:
            records = self.cursor.fetchall()
            col_names = [x[0] for x in self.cursor.description]
        self.close()
        if has_result:
            print("end blocking func")
            return [dict(zip(col_names, record)) for record in records]


