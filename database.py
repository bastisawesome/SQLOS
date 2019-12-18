import sqlite3

class Database():
    def __init__(self, _type='physical'):
        if _type == 'physical':
            self.db = sqlite3.connect('sqlos.db', detect_types=sqlite3.PARSE_DECLTYPES |
                sqlite3.PARSE_COLNAMES)
        elif _type == 'memory':
            self.db = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES |
                sqlite3.PARSE_COLNAMES)

        self.cur = self.db.cursor()
        self.log = [] #['CREATE TABLE users (username STRING NOT NULL)','SELECT * FROM users']

        self.num_logs = 0
        self.init_logs()
        self.init_table_meta()
    
    '''
    Checks that the table `logs` exists in the database. If it doesn't exist then it creates
    the table. If the table does exist then it populates `self.log` and sets the number of 
    logs for later.
    '''
    def init_logs(self):
        # So, I crashed Repl.it with this and then...
        # It fucking deleted everything!
        # So I had to write this twice.
        self.cur.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='logs' ''')
        
        if self.cur.fetchone()[0] == 1:
            # Table exists, let's pull logs!
            self.cur.execute('''SELECT * FROM logs''')
            
            # Store results
            res = self.cur.fetchall()
            self.num_logs = len(res)

            for log in res:
                self.log.append(*log)
        else:
            # Table doesn't exist, let's create it!
            self.cur.execute('''CREATE TABLE logs (message STRING NOT NULL)''')
    
    '''
    Checks that the table `table_meta` exists in the database. If it doesn't, it creates
    the necessary meta tables. These tables keep track of the existing tables and their
    columns. Each column contains a name, a type, if it allows null, and more information.
    '''
    def init_table_meta(self):
        # First check if the table_meta table exists
        self.cur.execute('''SELECT COUNT(name) FROM sqlite_master WHERE type='table' AND name='tables_meta' ''')

        if not self.cur.fetchone()[0]:
            # First, initialise the table_meta create statement
            c_table_meta = '''
            CREATE TABLE tables_meta (
                name STRING UNIQUE NOT NULL
            )
            '''
            
            c_column_meta = '''
            CREATE TABLE columns_meta (
                name STRING NOT NULL,
                type STRING NOT NULL,
                is_null INTEGER NOT NULL,
                is_unique INTEGER NOT NULL,
                is_primary_key INTEGER NOT NULL,
                table_name STRING NOT NULL,

                FOREIGN KEY(table_name) REFERENCES tables(name)
            )
            '''
            self.cur.execute(c_table_meta)
            self.cur.execute(c_column_meta)

    '''
    Executes SQL statements but does not commit to the database. The SQL statement passed
    in must already be formatted and cannot be a format string.
    @param sql Statement to be executed
    @param vals Tuple of values to pass into the template string
    @see self.commit
    '''
    def execute(self, sql, *vals):
        # Log the sql statements first
        tolog = sql
        for i in vals:
            tolog = tolog.replace('?', i, 1)
        self.log.append(tolog)

        # Execute the statements but raise if there's an error
        try:
            if 'CREATE' in sql.upper():
                self.add_table_meta(sql)
            elif 'DROP' in sql.upper():
                self.clear_table_meta(sql.split(' ')[2])

            self.cur.execute(sql, vals)
            
            # This statement is here in the event the user
            # executes a select statement.
            # It will either return an empty list or, on select
            # it will return all of the items in the list.
            return self.cur.fetchall()
        except sqlite3.OperationalError as e:
            # Reraise error
            raise e

    '''
    Commits changes to the database.
    '''
    def commit(self):
        self.db.commit()
    
    '''
    Inserts information into a meta table that keeps track of each column per table.
    This is used to handle selecting data and formatting it in a table display with
    header information.
    @param decl Table declaration SQL string
    '''
    def add_table_meta(self, decl: str):
        # Parse declaration to create the table's meta data
        data = decl.replace('CREATE', '').replace('TABLE', '').strip()
        data_dict = data.split(' ')
        table_name = data_dict[0]
        row_str = ' '.join(i for i in data_dict[1:])
        row_str = row_str.replace('(', '').replace(')', '').strip()
        table_rows = row_str.split(',')

        i_table_meta = '''
INSERT INTO tables_meta VALUES ('{}')'''.format(table_name)
        
        columns = []
        for row in table_rows:
            if 'FOREIGN KEY' in row.upper():
                continue
            row_s = row.strip().split(' ')
            row_name = row_s[0]
            row_type = row_s[1]
            row_nullable = not int('IS NULL' in row.upper())
            row_unique = int('UNIQUE' in row.upper())
            row_primary_key = int('PRIMARY KEY' in row.upper())

            columns.append([row_name, row_type, row_nullable, row_unique, row_primary_key, table_name])
        

        i_column_meta = '''
INSERT INTO columns_meta (name, type, is_null, is_unique, is_primary_key, table_name) VALUES ({})'''.format(','.join('?' for i in range(6)))
        
        self.cur.execute(i_table_meta)
        self.cur.executemany(i_column_meta, columns)
    
    '''
    Returns table meta data from the internal database.
    '''
    def get_table_meta(self, name):
        sql = '''
SELECT tables_meta.name, columns_meta.name, type, is_null, is_unique, is_primary_key FROM tables_meta
LEFT JOIN columns_meta
WHERE table_name = tables_meta.name
AND table_name = '{}'
'''.format(name)

        return self.cur.execute(sql).fetchall()
    
    def clear_table_meta(self, name):
        clear_table = '''
DELETE FROM tables_meta WHERE name='{}'
'''.format(name)
        
        clear_columns = '''
DELETE FROM columns_meta WHERE table_name='{}'
'''.format(name)

        self.cur.execute(clear_table)
        self.cur.execute(clear_columns)
        self.db.commit()
    
    '''
    Write logs to the databse then close the datatbase
    '''
    def __del__(self):
        # Let's save those logs!
        # Create a tuple for our logs
        logs = [tuple([log]) for log in self.log[self.num_logs:]]

        self.cur.executemany('''INSERT INTO logs VALUES (?)''', logs)
        self.db.commit()
        
        #self.db.close()