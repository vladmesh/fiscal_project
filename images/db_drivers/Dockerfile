FROM fiscal_python_base

# Скачиваем драйвера и софт для оракла
# TODO Тут мы на ссылку полагаемся, это не очень хорошо, мб лучше создать отдельный образ и сделать так:
# https://blogs.oracle.com/opal/post/part-1-docker-for-oracle-database-applications-in-nodejs-and-python
WORKDIR    /opt/oracle
RUN        apt-get update && apt-get install -y libaio1 wget unzip \
            && wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip \
            && unzip instantclient-basiclite-linuxx64.zip \
            && rm -f instantclient-basiclite-linuxx64.zip \
            && cd /opt/oracle/instantclient* \
            && rm -f *jdbc* *occi* *mysql* *README *jar uidrvci genezi adrci \
            && echo /opt/oracle/instantclient* > /etc/ld.so.conf.d/oracle-instantclient.conf \
            && ldconfig
WORKDIR    /
# Add SQL Server ODBC Driver 17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated msodbcsql17
RUN ACCEPT_EULA=Y apt-get install -y --allow-unauthenticated mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

#Скачиваем драйвера для odbc
RUN apt-get  install -y libc-dev libpq-dev  libffi-dev libxml2 unixodbc-dev

COPY requirements.txt .
RUN pip install -r requirements.txt