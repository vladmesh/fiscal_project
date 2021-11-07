FROM fiscal_python_db_drivers:latest
WORKDIR code
EXPOSE 8085
COPY revise_service revise_service
COPY core revise_service/core
CMD ["python", "revise_service/Main.py"]
