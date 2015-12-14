# grow_mustache

Python helper functions for generating Mustache templates

Currently only has a demo for sqlite3.

To get started:

    pip install -r requirements.txt

Demo

    python db2template.py

Or:

    >>> import sqlite3
    >>> from db2template import result_to_empty_template
    >>> db = sqlite3.connect(':memory:')
    >>> c = db.cursor()
    >>> template = result_to_empty_template(c, 'SELECT * FROM sqlite_master')
    >>> print template
    <table border="1" class="sortable">
        <thead>
            <tr>
                <th>type</th>
                <th>name</th>
                <th>tbl_name</th>
                <th>rootpage</th>
                <th>sql</th>

            </tr>
        </thead>

        <tbody>
            {{#rows}}
            <tr>
                <td>{{type}}</td>
                <td>{{name}}</td>
                <td>{{tbl_name}}</td>
                <td>{{rootpage}}</td>
                <td>{{sql}}</td>

                </tr>
            {{/rows}}
        </tbody>
    </table>
