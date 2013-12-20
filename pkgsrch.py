import psycopg2, argparse
from subprocess import call

def main(**args):

    conn = psycopg2.connect("dbname=pkgdb")

    cur = conn.cursor()

    if args['init']:
        initializeDB(cur)

    # Pass data to fill a query placeholders and let Psycopg perform
    # the correct conversion (no more SQL injections!)
    cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)",
               (100, "abc'def"))

    # Query the database and obtain data as Python objects
    cur.execute("SELECT * FROM test;")
    cur.fetchone()

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

def initializeDB(cur):
    if tableExists('test', cur):
        cur.execute("""DROP TABLE test;""")

    # Execute a command: this creates a new table
    cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

def tableExists(tableName, cur):
    """Return true if the table exists, false otherwise."""
    cur.execute("""SELECT EXISTS(SELECT 1 
                          FROM information_schema.tables
                          WHERE table_catalog='pkgdb' AND 
                          table_schema='public' AND
                          table_name=%s);""", ('test',))
    return cur.fetchone()[0]

if __name__ == '__main__':
    # Command line argument handling.
    parser = argparse.ArgumentParser(
            description='Search the package cache', version='0.1')
    parser.add_argument('-i', '--init',
                        help='Initialize database', action="store_true")
    args = parser.parse_args()
    main(**vars(args))
