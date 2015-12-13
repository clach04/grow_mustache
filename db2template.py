#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
"""Generate a Mustache template from a table.
Given a db connection, SQL query, and optional bind params

"""

import os
import sys

import stache  # from https://github.com/clach04/Stache


def select_dict_from_db_generator(cursor, sql_query, bind_params=None, dict_constructor=dict):
    """Runs select and returns iterator of dicts. Uses a generator
    """
    if bind_params is None:
        # Some DBI drivers freak on None/Empty bind params
        cursor.execute(sql_query)
    else:
        cursor.execute(sql_query, bind_params)
    # Note, most DBI drivers actually have an iterator interface
    row = cursor.fetchone()
    while row is not None:
        yield dict_constructor(zip(map(lambda x:x[0], cursor.description), row))
        row = cursor.fetchone()

def result_to_empty_template(cursor, sql_query, bind_params=None, dict_constructor=dict):
    """Runs select and returns Mustache template.
    """
    if bind_params is None:
        # Some DBI drivers freak on None/Empty bind params
        cursor.execute(sql_query)
    else:
        cursor.execute(sql_query, bind_params)
    col_names = []
    template_dict = {}
    template_dict['column_names'] = []
    # PEP 0249 description
    for name, type_code, display_size, internal_size, precision, scale, null_ok in cursor.description:
        # for now ignore type, etc.
        col_names.append(name)
        template_dict['column_names'].append({'name': name})
    cursor.close()  # do NOT need results

    # Stache doesn't support alternative delimiters, nor escaping
    # of delimiters for literals. Workaround this using:
    template_dict['open_stache'] = '{{'
    template_dict['close_stache'] = '}}'

    template_str = """<table border="1" class="sortable">
    <thead>
        <tr>
            {{#column_names}}<th>{{name}}</th>
            {{/column_names}}
        </tr>
    </thead>

    <tbody>
        {{open_stache}}#rows{{close_stache}}
        <tr>
        {{#column_names}}<td>{{open_stache}}{{name}}{{close_stache}}</td>
        {{/column_names}}
        </tr>
        {{open_stache}}/rows{{close_stache}}
    </tbody>
</table>

"""

    result = stache.Stache().render(template_str, template_dict)
    return result

def demo(setup_func):
    db = setup_func()

    sql = """
    SELECT * FROM some_table
    """
    bind_params = None

    try:
        c = db.cursor()
        tmp_template = result_to_empty_template(c, sql, bind_params)
        print tmp_template

        rows = select_dict_from_db_generator(c, sql, bind_params)
        print '*' * 65
        for x in rows:
            print x
        print '*' * 65

        rows = select_dict_from_db_generator(c, sql, bind_params)
        template_dict = {'rows': rows}  # NOTE rows is an iterator NOT a list
        final = stache.Stache().render(tmp_template, template_dict)
        print final

        c.close()
        db.commit()  # or rollback
    finally:
        db.close()

def demo_sqlite3():
    import sqlite3

    dbname = ':memory:'
    db = sqlite3.connect(dbname)
    c = db.cursor()

    c.execute("""CREATE TABLE some_table (
    filename  TEXT,
    mtime  TEXT,
    filesize integer,
    checksum  TEXT
);
    """)
    c.execute(""" INSERT INTO some_table VALUES ('hello.txt', '2001-01-02 03:04:05', '99', NULL) """)
    c.execute(""" INSERT INTO some_table VALUES ('world.txt', '2006-07-08 09:10:11', '99', NULL) """)
    c.close()
    return db


def main(argv=None):
    if argv is None:
        argv = sys.argv

    demo(demo_sqlite3)

    return 0


if __name__ == "__main__":
    sys.exit(main())
