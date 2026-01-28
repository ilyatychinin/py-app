docker container run --name test-postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=py-app-db \
  -v postgres_data:/var/lib/postgresql/data \
  -v $(pwd)/schema.sql:/docker-entrypoint-initdb.d/schema.sql \
  postgres:18
