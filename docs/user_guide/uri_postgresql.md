# Database URI

---

## **PostgreSQL**

PySQLXEngine is based on the [official PostgreSQL format](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING) for connection URLs, but does not support all arguments and includes additional arguments such as schema. Here's an overview of the components needed for a PostgreSQL connection URL:

<img src="../img/postgresql_uri.png" alt="PostgreSQL uri example">

### **Base URL and path**

Here is an example of the structure of the base URL and the path using placeholder values in uppercase letters:

```text
postgresql://USER:PASSWORD@HOST:PORT/DATABASE
```

The following components make up the base URL of your database, they are always required:

| Name     | Placeholder | Description                                                                                                   |
|:--------:|:-----------:|---------------------------------------------------------------------------------------------------------------|
| Host     | `HOST`      | IP address/domain of your database server, e.g. localhost                                                     |
| Port     | `PORT`      | Port on which your database server is running, e.g. 5432                                                      |
| User     | `USER`      | Name of your database user, e.g. janedoe                                                                      |
| Password | `PASSWORD`  | Password for your database user                                                                               |
| Database | `DATABASE`  | Name of the [database](https://www.postgresql.org/docs/12/manage-ag-overview.html) you want to use, e.g. mydb |


### **Arguments**

A connection URL can also take arguments. Here is the same example from above with placeholder values in uppercase letters for three arguments:

```text
postgresql://USER:PASSWORD@HOST:PORT/DATABASE?KEY1=VALUE&KEY2=VALUE&KEY3=VALUE
```

Sintax:

* Example: `KEY1`**=**`VALUE`**&**`KEY2`**=**`VALUE`
* Equal sign `=` is used to separate the `key` from the `value`
* Ampersand `&` is used to separate the arguments


The following arguments can be used:

| Argument name    | Required | Default              | Description                                                                                                       |
|:-----------------|:--------:|:--------------------:|-------------------------------------------------------------------------------------------------------------------|
| schema           | Yes      | public               | Name of the [schema](https://www.postgresql.org/docs/12/ddl-schemas.html) you want to use, e.g. myschema          |
| connect_timeout  | No       | 5                    | Maximum number of seconds to wait for a new connection to be opened, 0 means no timeout                           |
| sslmode          | No       | prefer               | Configures whether to use TLS. Possible values: prefer, disable, require                                          |
| sslcert          | No       |                      | Path of the server certificate                                                                                    |
| sslidentity      | No       |                      | Path to the PKCS12 certificate                                                                                    |
| sslpassword      | No       |                      | Password that was used to secure the PKCS12 file                                                                  |
| sslaccept        | No       | accept_invalid_certs | Configures whether to check for missing values in the certificate. Possible values: accept_invalid_certs, strict  |
| host             | No       |                      | Points to a directory that contains a socket to be used for the connection                                        |
| socket_timeout   | No       |                      | Maximum number of seconds to wait until a single query terminates                                                 |
| application_name | No       |                      | Since 3.3.0: Specifies a value for the application_name configuration parameter                                   |
| channel_binding  | No       | prefer               | Since 4.8.0: Specifies a value for the channel_binding configuration parameter                                    |
| options          | No       |                      | Since 3.8.0: Specifies command line options to send to the server at connection start                             |

#### Configuring an SSL connection
You can add various parameters to the connection URL if your database server uses SSL. Here's an overview of the possible parameters:

* `sslmode=(disable|prefer|require)`:
    - `prefer` (default): Prefer TLS if possible, accept plain text connections.
    - `disable`: Do not use TLS.
    - `require`: Require TLS or fail if not possible.
    
* `sslcert=<PATH>`: Path to the server certificate. This is the root certificate used by the database server to sign the client certificate. You need to provide this if the certificate doesn't exist in the trusted certificate store of your system. For Google Cloud this likely is server-ca.pem.

* `sslidentity=<PATH>`: Path to the PKCS12 certificate database created from client cert and key. This is the SSL identity file in PKCS12 format which you will generate using the client key and client certificate. It combines these two files in a single file and secures them via a password (see next parameter). You can create this file using your client key and client certificate by using the following command (using `openssl`):


```sh
openssl pkcs12 -export -out client-identity.p12 -inkey client-key.pem -in client-cert.pem
```

* `sslpassword=<PASSWORD>`: Password that was used to secure the PKCS12 file. The openssl command listed in the previous step will ask for a password while creating the PKCS12 file, you will need to provide that same exact password here.

* `sslaccept=(strict|accept_invalid_certs)`:
    - strict: Any missing value in the certificate will lead to an error. For Google Cloud, especially if the database doesn't have a domain name, the certificate might miss the domain/IP address, causing an error when connecting.
    - accept_invalid_certs (default): Bypass this check. Be aware of the security consequences of this setting.

Your database connection URL will look similar to this:

```text
postgresql://USER:PASSWORD@HOST:PORT/DATABASE?sslidentity=client-identity.p12&sslpassword=mypassword&sslcert=rootca.cert
```


#### Connecting via sockets
To connect to your PostgreSQL database via sockets, you must add a host field as a query parameter to the connection URL (instead of setting it as the host part of the URI). The value of this parameter then must point to the directory that contains the socket, e.g.: `postgresql://USER:PASSWORD@localhost/database?host=/var/run/postgresql/`

Note that localhost is required, the value itself is ignored and can be anything.