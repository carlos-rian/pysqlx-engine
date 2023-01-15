# JSON Support


PySQLX-Engine has support for converting various types to JSON dumps. This dump is accepted into your database as a string.

Some databases have native support for JSON, but some don't. When you send a `parameter` of type `list` or `dict` to the database, 
PySQLX-Engine will convert it into a JSON dump and send it to the database as a string.

## JSON Encoding Types

| Python Types | JSON Types                                 | IN                                               | OUT                                   |
|--------------|--------------------------------------------|--------------------------------------------------|---------------------------------------|
| bytes        | String(Hex)                                | b'super bytes'                                   | "7375706572206279746573"              |
| uuid         | String                                     | UUID('ae77f0f3-0313-4ebe-9d1f-319d8fbe94d6')     | "ae77f0f3-0313-4ebe-9d1f-319d8fbe94d6"|
| time         | String                                     | datetime.time(12, 20, 50)                        | "12:20:50"                            |
| date         | String                                     | datetime.date(2023, 1, 15)                       | "2023-01-15"                          |
| datetime     | String                                     | datetime.datetime(2023, 1, 15, 16, 7, 1, 441234) | "2023-01-15 16:07:01.441234"          |
| Decimal      | String                                     | Decimal('1.23')                                  | '1.23'                                |
| None         | Null                                       | None                                             | null                                  |
| bool         | Bool                                       | True                                             | true                                  |
| str          | String                                     | 'value'                                          | "value"                               |
| int          | Int                                        | 123                                              | 123                                   |
| float        | Float                                      | 32.33                                            | 32.33                                 |
| *            | Try converting using standard `JSON Dumps` |                                                  |                                       |