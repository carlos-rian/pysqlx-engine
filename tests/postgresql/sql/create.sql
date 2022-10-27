create type colors as enum ('blue', 'red', 'gray', 'black');

create table pysqlx_table
(
    type_int           integer,
    type_smallint      smallint,
    type_bigint        bigint,
    --
    type_serial        serial,
    type_smallserial   smallserial,
    type_bigserial     bigserial,
    --
    type_numeric       numeric,
    type_float         float            not null,
    type_double        double precision null,
    type_money         money,
    --
    type_char          char,
    type_varchar       varchar(100),
    type_text          text,
    --
    type_boolean       boolean,
    --
    type_date          date,
    type_time          time,
    type_datetime      timestamp,
    type_datetimetz    timestamptz,
    --
    type_interval      interval,
    --
    type_enum          colors,
    --
    type_uuid          uuid,
    --
    type_json          json,
    --
    type_jsonb         jsonb,
    --
    type_xml           xml,
    --
    type_inet          inet,
    type_cidr          cidr,
    type_macaddr       macaddr,
    --
    type_polygon       polygon,
    --
    type_line          line,
    type_lseg          lseg,
    --
    type_box           box,
    --
    type_bytes         bytea,
    --
    type_tsvector      tsvector,
    type_tsquery       tsquery,
    --
    type_array_text    text[],
    type_array_integer integer[],
    type_array_date    date[],
    type_array_uuid    uuid[]
);