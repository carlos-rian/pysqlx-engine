# Supported Databases

Currently supports the following databases:

| **Provider**                                          | **Database**                                                                | **Version**              |
|-------------------------------------------------------|-----------------------------------------------------------------------------|--------------------------|
| [**postgresql** ](https://www.postgresql.org)         | [PostgreSQL](https://www.postgresql.org)                                    | 9.4+, 10, 11, 12, 13, 14 |
| [**mysql**](https://www.mysql.com)                    | [MySQL](https://www.mysql.com)                                              | 5.6, 5.7, 8              |
| [**mysql**](https://www.mysql.com)                    | [MariaDB](https://mariadb.org/)                                             | 10                       |
| [**sqlite**](https://www.sqlite.org/index.html)       | [SQLite](https://www.sqlite.org/index.html)                                 | *                        |
| [**postgresql** ](https://www.postgresql.org)         | [AWS Aurora](https://aws.amazon.com/pt/rds/aurora/)                         | *                        |
| [**postgresql** ](https://www.postgresql.org)         | [AWS Aurora Serverless](https://aws.amazon.com/pt/rds/aurora/serverless/) ¹ | *                        |
| [**sqlserver**](https://www.microsoft.com/sql-server) | [Microsoft SQL Server](https://www.microsoft.com/sql-server)                | 17, 19                   |
| [**sqlserver**](https://www.microsoft.com/sql-server) | [Azure SQL](https://azure.microsoft.com/pt-br/products/azure-sql/database/) | *                        |


An asterisk (*) indicates that the version number is not relevant; either all versions are supported, there is not a public version number, etc.

¹ This does not include support for Data API for Aurora Serverless.