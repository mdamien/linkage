CREATE DATABASE linkage;
CREATE USER linkage WITH PASSWORD 'linkage';
ALTER ROLE linkage SET client_encoding TO 'utf8';
ALTER ROLE linkage SET default_transaction_isolation TO 'read committed';
ALTER ROLE linkage SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE linkage TO linkage;
