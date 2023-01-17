# Database URI

---
## **MySQL**

Here's an overview of the components needed for a MySQL connection URL:

<img src="./img/mysql_uri.png" alt="MySQL uri example">

### **Base URL and path**

Here is an example of the structure of the base URL and the path using placeholder values in uppercase letters:

```text
mysql://USER:PASSWORD@HOST:PORT/DATABASE
```

The following components make up the base URL of your database, they are always required:

| Name     | Placeholder | Description                                                |
|:--------:|:-----------:|------------------------------------------------------------|
| Host     | `HOST`      | IP address/domain of your database server, e.g. localhost  |
| Port     | `PORT`      | Port on which your database server is running, e.g. 5432   |
| User     | `USER`      | Name of your database user, e.g. janedoe                   |
| Password | `PASSWORD`  | Password for your database user                            |
| Database | `DATABASE`  | Name of the database you want to use, e.g. mydb            |


### **Arguments**

A connection URL can also take arguments. Here is the same example from above with placeholder values in uppercase letters for three arguments:

```text
mysql://USER:PASSWORD@HOST:PORT/DATABASE?KEY1=VALUE&KEY2=VALUE&KEY3=VALUE
```

Sintax:

* Example: `KEY1`**=**`VALUE`**&**`KEY2`**=**`VALUE`
* Equal sign `=` is used to separate the `key` from the `value`
* Ampersand `&` is used to separate the arguments

| Argument name   | Required | Default              | Description                                                                                                       |
|-----------------|:--------:|:--------------------:|-------------------------------------------------------------------------------------------------------------------|
| connect_timeout | No       | 5                    | Maximum number of seconds to wait for a new connection to be opened, 0 means no timeout                           |
| sslcert         | No       |                      | Path to the server certificate.                                                                                   |
| sslidentity     | No       |                      | Path to the PKCS12 certificate                                                                                    |
| sslpassword     | No       |                      | Password that was used to secure the PKCS12 file                                                                  |
| sslaccept       | No       | accept_invalid_certs | Configures whether to check for missing values in the certificate. Possible values: accept_invalid_certs, strict  |
| socket          | No       |                      | Points to a directory that contains a socket to be used for the connection                                        |
| socket_timeout  | No       |                      | Number of seconds to wait until a single query terminates                                                         |

#### **Configuring an SSL connection**
You can add various parameters to the connection URL if your database server uses SSL. Here's an overview of the possible parameters:

* `sslcert=<PATH>`: Path to the server certificate. This is the root certificate used by the database server to sign the client certificate. You need to provide this if the certificate doesn't exist in the trusted certificate store of your system. For Google Cloud this likely is server-ca.pem.

* `sslidentity=<PATH>`: Path to the PKCS12 certificate database created from client cert and key. This is the SSL identity file in PKCS12 format which you will generate using the client key and client certificate. It combines these two files in a single file and secures them via a password (see next parameter). You can create this file using your client key and client certificate by using the following command (using `openssl`):

```sh
openssl pkcs12 -export \
    -out client-identity.p12 \
    -inkey client-key.pem \
    -in client-cert.pem
```

* `sslpassword=<PASSWORD>`: Password that was used to secure the PKCS12 file. The openssl command listed in the previous step will ask for a password while creating the PKCS12 file, you will need to provide that same exact password here.

* `sslaccept=(strict|accept_invalid_certs)`:

    - `strict`: Any missing value in the certificate will lead to an error. For Google Cloud, especially if the database doesn't have a domain name, the certificate might miss the domain/IP address, causing an error when connecting.
    
    - `accept_invalid_certs (default)`: Bypass this check. Be aware of the security consequences of this setting.

Your database connection URL will look similar to this:

```text
mysql://USER:PASSWORD@HOST:PORT/DATABASE?sslidentity=client-identity.p12&sslpassword=mypassword&sslcert=rootca.cert
```


#### **Connecting via sockets**

To connect to your MySQL database via sockets, you must add a socket field as a query parameter to the connection URL (instead of setting it as the host part of the URI). The value of this parameter then must point to the directory that contains the socket, e.g.: `mysql://USER:POST@localhost/database?socket=/var/run/mysql/`

Note that localhost is required, the value itself is ignored and can be anything.
