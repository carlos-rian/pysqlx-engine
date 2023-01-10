# Microsoft SQL Server

---
## **Microsoft SQL Server**

### **Connection details**
The connection URL used to connect to an Microsoft SQL Server database follows the [JDBC standard](https://learn.microsoft.com/en-us/sql/connect/jdbc/building-the-connection-url?view=sql-server-ver15).

The following example uses SQL authentication (username and password) with an enabled TLS encrypted connection:

```text
sqlserver://HOST:PORT;database=DATABASE;user=USER;password=PASSWORD;encrypt=true
```

#### **Using [integrated security](https://learn.microsoft.com/en-us/previous-versions/dotnet/framework/data/adonet/sql/authentication-in-sql-server) (Windows only)**

The following example uses the currently logged in Windows user to log in to Microsoft SQL Server:

```text
sqlserver://localhost:1433;initialCatalog=sample;integratedSecurity=true;trustServerCertificate=true;
```

The following example uses a specific Active Directory user to log in to Microsoft SQL Server:
    
```text
sqlserver://localhost:1433;initialCatalog=sample;integratedSecurity=true;username=prisma;password=aBcD1234;trustServerCertificate=true;
```

#### **Using SQL Browser to connect to a named instance**

The following example connects to a named instance of Microsoft SQL Server (mycomputer\sql2019) using integrated security:

```text
sqlserver://mycomputer\sql2019;initialCatalog=sample;integratedSecurity=true;trustServerCertificate=true;
```

### **Arguments**

| Argument   name                                      | Required          | Default | Comments                                                                                                                                                                                                                                                                                                                              |
|------------------------------------------------------|-------------------|---------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| database/initial   catalog                           | No                | master  | The database to   connect to.                                                                                                                                                                                                                                                                                                         |
| username/user/uid/userid                             | No - see Comments |         | SQL Server login (such   as sa) or a valid Windows (Active   Directory) username if integratedSecurity is set to true (Windows only).                                                                                                                                                                                                 |
| password/pwd                                         | No - see Comments |         | Password for SQL   Server login or Windows   (Active Directory) username if integratedSecurity is set to true (Windows only).                                                                                                                                                                                                         |
| encrypt                                              | No                | true    | Configures whether to   use TLS all the time, or only for the login procedure, possible values: true (use always), false (only for login   credentials).                                                                                                                                                                              |
| integratedSecurity                                   | No                |         | [Enables Windows   authentication](https://learn.microsoft.com/en-us/previous-versions/dotnet/framework/data/adonet/sql/authentication-in-sql-server) (integrated security), possible values: true, false, yes, no. If set to true or yes and username and password are present, login is performed through Windows Active Directory. |
| connectTimeout                                       | No                | 5       | Maximum number of   seconds to wait for a new connection                                                                                                                                                                                                                                                                              |
| schema                                               | No                | dbo     | Added as a prefix to   all the queries if schema name is not the default.                                                                                                                                                                                                                                                             |
| loginTimeout/connectTimeout/connectionTimeout        | No                |         | Number of seconds to   wait for login to succeed.                                                                                                                                                                                                                                                                                     |
| socketTimeout                                        | No                |         | Number of seconds to   wait for each query to succeed.                                                                                                                                                                                                                                                                                |
| isolationLevel                                       | No                |         | Sets [transaction isolation   level](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql?view=sql-server-ver15).                                                                                                                                                                      |
| ApplicationName/Application   Name(case insensitive) | No                |         | Sets the application   name for the connection. Since version 2.28.0.                                                                                                                                                                                                                                                                 |
| trustServerCertificate                               | No                | false   | Configures whether to   trust the server certificate.                                                                                                                                                                                                                                                                                 |
| trustServerCertificateCA                             | No                |         | A   path to a certificate authority file to be used instead of the system   certificates to authorize the server certificate. Must be either in pem, crt or der format. Cannot be used together with trustServerCertificate parameter.                                                                                                |