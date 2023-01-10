# Microsoft SQL Server on Docker

---

## **SQL Server on Docker**

To run a Microsoft SQL Server container image with Docker:

1. Install and set up [Docker](https://docs.docker.com/get-docker/)

2. Run the following command in your terminal to download the Microsoft SQL Server 2019 image:

    <div class="termy">

    ```console
    $ docker pull mcr.microsoft.com/mssql/server:2019-latest

    ...
    ```
    </div>


3. Create an instance of the container image, replacing the value of SA_PASSWORD with a password of your choice:

    <div class="termy">

    ```console
    $ docker run --name sql_container -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=myPassword' -p 1433:1433 -d mcr.microsoft.com/mssql/server:2019-latest

    ...
    ```
    </div>

4. [Follow Microsoft's instructions](https://learn.microsoft.com/en-us/sql/linux/quickstart-install-connect-docker?view=sql-server-ver15&pivots=cs1-cmd#connect-to-sql-server) to connect to SQL Server and use the `sqlcmd` tool, replacing the image name and password with your own.

5. From the `sqlcmd` command prompt, create a new database:

    <div class="termy">

    ```console
    CREATE DATABASE quickstart
    GO

    ...

    ```
    </div>

6. Run the following command to check that your database was created successfully:

    <div class="termy">

    ```console

    sp_databases
    GO

    ...
    ```
    </div>

### Connection URL credentials

Based on this example, your credentials are:

* **Username**: `sa`
* **Password**: `myPassword`
* **Database**: `quickstart`
* **Port**: `1433`