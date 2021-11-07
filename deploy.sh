docker build -t fiscal_python_base images/base/
docker build -t fiscal_python_db_drivers images/db_drivers
docker-compose build
docker-compose up