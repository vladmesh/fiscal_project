FROM fiscal_python_db_drivers:latest
WORKDIR code
EXPOSE 8086
COPY fink_service fink_service
COPY core fink_service/core
CMD ["python", "fink_service/Main.py"]
