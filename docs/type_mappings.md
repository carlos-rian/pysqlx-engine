# Type mappings

---

## **PostgreSQL**

When introspecting a PostgreSQL database, the database types are mapped to PySQLXEngine according to the following table:

| PostgreSQL   (Type / Aliases)            | Python      | Supported  |
|------------------------------------------|-------------|:----------:|
| bigint / int8                            | int         |✔️          |
| boolean / bool                           | bool        |✔️          |
| timestamp with time   zone / timestamptz | datetime    |✔️          |
| time without time zone / time            | time        |✔️          |
| time with time zone / timetz             | time        |✔️          |
| numeric(p,s) / decimal(p,s)              | decimal     |✔️          |
| real / float, float4                     | float       |✔️          |
| double precision / float8                | float       |✔️          |
| smallint / int2                          | Int         |✔️          |
| integer / int, int4                      | Int         |✔️          |
| smallserial / serial2                    | Int         |✔️          |
| serial / serial4                         | Int         |✔️          |
| bigserial / serial8                      | Int         |✔️          |
| character(n) / char(n)                   | str         |✔️          |
| character   varying(n) / varchar(n)      | str         |✔️          |
| money                                    | decimal     |✔️          |
| text                                     | str         |✔️          |
| timestamp                                | datetime    |✔️          |
| date                                     | date        |✔️          |
| enum                                     | str         |✔️          |
| inet                                     | str         |✔️          |
| bit(n)                                   | str         |✔️          |
| bit varying(n)                           | str         |✔️          |
| oid                                      | int         |✔️          |
| uuid                                     | uuid        |✔️          |
| json                                     | dict/list   |✔️          |
| jsonb                                    | dict/list   |✔️          |
| bytea                                    | bytes       |✔️          |
| xml                                      | str         |✔️          |
| Array types                              | tuple       |✔️          |
| citext                                   | str         |✔️ *        |
| interval                                 | Unsupported |Not  yet    |
| cidr                                     | Unsupported |Not  yet    |
| macaddr                                  | Unsupported |Not  yet    |
| tsvector                                 | Unsupported |Not  yet    |
| tsquery                                  | Unsupported |Not  yet    |
| int4range                                | Unsupported |Not  yet    |
| int8range                                | Unsupported |Not  yet    |
| numrange                                 | Unsupported |Not  yet    |
| tsrange                                  | Unsupported |Not  yet    |
| tstzrange                                | Unsupported |Not  yet    |
| daterange                                | Unsupported |Not  yet    |
| point                                    | Unsupported |Not  yet    |
| line                                     | Unsupported |Not  yet    |
| lseg                                     | Unsupported |Not  yet    |
| box                                      | Unsupported |Not  yet    |
| path                                     | Unsupported |Not  yet    |
| polygon                                  | Unsupported |Not  yet    |
| circle                                   | Unsupported |Not  yet    |
| Composite   types                        | n/a         |Not  yet    |
| Domain   types                           | n/a         |Not  yet    |

---

## **MySQL**

When introspecting a MySQL database, the database types are mapped to PySQLXEngine according to the following table:

| MySQL (Type / Aliases)| Python      | Supported  |
|-----------------------|-------------|:----------:|
| serial                | int         |✔️          |
| bigint                | int         |✔️          |
| bigint unsigned       | int         |✔️          |
| bit                   | bytes       |✔️          |
| boolean \| tinyint(1) | bool        |✔️          |
| varbinary             | bytes       |✔️          |
| longblob              | bytes       |✔️          |
| tinyblob              | bytes       |✔️          |
| mediumblob            | bytes       |✔️          |
| blob                  | bytes       |✔️          |
| binary                | bytes       |✔️          |
| date                  | **datetime**|✔️          |
| datetime              | datetime    |✔️          |
| timestamp             | datetime    |✔️          |
| time                  | time        |✔️          |
| decimal(a,b)          | decimal     |✔️          |
| numeric(a,b)          | decimal     |✔️          |
| enum                  | str         |✔️          |
| float                 | float       |✔️          |
| double                | float       |✔️          |
| smallint              | int         |✔️          |
| smallint unsigned     | int         |✔️          |
| mediumint             | int         |✔️          |
| mediumint unsigned    | int         |✔️          |
| int                   | int         |✔️          |
| int unsigned          | int         |✔️          |
| tinyint               | int         |✔️          |
| tinyint unsigned      | int         |✔️          |
| year                  | int         |✔️          |
| json                  | dict/list   |✔️          |
| char                  | str         |✔️          |
| varchar               | str         |✔️          |
| tinytext              | str         |✔️          |
| text                  | str         |✔️          |
| mediumtext            | str         |✔️          |
| longtext              | str         |✔️          |
| set                   | Unsupported |Not yet     |
| geometry              | Unsupported |Not yet     |
| point                 | Unsupported |Not yet     |
| linestring            | Unsupported |Not yet     |
| polygon               | Unsupported |Not yet     |
| multipoint            | Unsupported |Not yet     |
| multilinestring       | Unsupported |Not yet     |
| multipolygon          | Unsupported |Not yet     |
| geometrycollection    | Unsupported |Not yet     |

---

## **Microsoft SQL Server**

When introspecting a Microsoft SQL Server database, the database types are mapped to PySQLXEngine according to the following table:

| Microsoft   SQL Server | Python   | Supported |
|------------------------|----------|-----------|
| char                   | str      | ✔️         |
| nchar                  | str      | ✔️         |
| varchar                | str      | ✔️         |
| nvarchar               | str      | ✔️         |
| text                   | str      | ✔️         |
| ntext                  | str      | ✔️         |
| xml                    | str      | ✔️         |
| uniqueidentifier       | uuid     | ✔️         |
| tinyint                | bool     | ✔️         |
| bit                    | bool     | ✔️         |
| int                    | int      | ✔️         |
| smallint               | int      | ✔️         |
| tinyint                | int      | ✔️         |
| bit                    | int      | ✔️         |
| bigint                 | int      | ✔️         |
| decimal/numeric        | decimal  | ✔️         |
| money                  | decimal  | ✔️         |
| date                   | date     | ✔️         |
| time                   | time     | ✔️         |
| datetime               | datetime | ✔️         |
| datetime2              | datetime | ✔️         |
| smalldatetime          | datetime | ✔️         |
| datetimeoffset         | datetime | ✔️         |
| binary                 | bytes    | ✔️         |
| varbinary              | bytes    | ✔️         |
| image                  | bytes    | ✔️         |

---

## **SQLite**

When introspecting a SQLite database, the database types are mapped to PySQLXEngine according to the following table:

| SQLite (Type / Aliases) | Python      | Supported  |
|-------------------------|-------------|:----------:|
| TEXT                    | str         |✔️          |
| BOOLEAN                 | bool        |✔️          |
| INTEGER                 | int         |✔️          |
| NUMERIC                 | decimal     |✔️          |
| REAL                    | float       |✔️          |
| DECIMAL                 | decimal     |✔️          |
| BLOB                    | bytes       |✔️          |
