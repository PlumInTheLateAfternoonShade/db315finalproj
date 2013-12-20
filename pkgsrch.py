import psycopg2, argparse
from subprocess import call

def main(**args):

    conn = psycopg2.connect("dbname=pkgdb")

    cur = conn.cursor()

    if args['init']:
        initializeDB(cur)

    conn.commit()
    cur.close()
    conn.close()

def initializeDB(cur):
    """Drop tables if they already exist. Create them. Populate them."""
    [dropTableIfExists(tn, cur) for tn in ['package', 'fileinfo',
        'descriptor', 'compatibility',
        'maintains', 'maintainer']]
    [dropSequenceIfExists(sn, cur) for sn in ['pack_id_seq',
        'maint_id_seq']]
    
    cur.execute(
            """CREATE SEQUENCE pack_id_seq;
        CREATE TABLE package (
                id integer NOT NULL DEFAULT nextval('pack_id_seq')
                    PRIMARY KEY,
                name text,
                installed boolean
        );""")

    cur.execute(
            """CREATE TABLE fileinfo (
                path text,
                sizeDownload integer,
                sizeInstalled integer,
                pack integer,
                FOREIGN KEY(pack) REFERENCES package(id)
        );""")

    cur.execute("""CREATE TABLE descriptor (
                description text,
                tag text[],
                section text,
                manpage text,
                relevancy integer,
                pack integer,
                FOREIGN KEY(pack) REFERENCES package(id)
        );""")

    cur.execute("""CREATE TABLE compatibility (
                architecture text,
                version text,
                dependencies text[],
                priority text,
                branch text,
                packageSite text,
                pack integer,
                FOREIGN KEY(pack) REFERENCES package(id)
        );""")

    cur.execute("""CREATE SEQUENCE maint_id_seq;
        CREATE TABLE maintainer (
                mid integer NOT NULL DEFAULT
                    nextval('maint_id_seq') PRIMARY KEY,
                name text,
                email text,
                homepage text
        );""")

    cur.execute("""CREATE TABLE maintains (
            maint integer,
            FOREIGN KEY(maint) REFERENCES maintainer(mid),
            pack integer,
            FOREIGN KEY(pack) REFERENCES package(id)
        );""")


def tableExists(tableName, cur):
    """Return true if the table exists, false otherwise."""
    cur.execute("""SELECT EXISTS(SELECT 1 
                          FROM information_schema.tables
                          WHERE table_catalog='pkgdb' AND 
                          table_schema='public' AND
                          table_name=%s);""", (tableName,))
    return cur.fetchone()[0]

def sequenceExists(tableName, cur):
    """Return true if the table exists, false otherwise."""
    cur.execute("""SELECT EXISTS(SELECT 1 
                          FROM information_schema.sequences
                          WHERE sequence_catalog='pkgdb' AND 
                          sequence_schema='public' AND
                          sequence_name=%s);""", (tableName,))
    return cur.fetchone()[0]

def dropTableIfExists(tableName, cur):
    """Drop a table if it exists."""
    if tableExists(tableName, cur):
        cur.execute('DROP TABLE ' + tableName + ' CASCADE;')
        return True
    return False

def dropSequenceIfExists(seqName, cur):
    """Drop a sequence if it exists."""
    if sequenceExists(seqName, cur):
        cur.execute('DROP SEQUENCE ' + seqName + ' CASCADE;')
        return True
    return False

if __name__ == '__main__':
    # Command line argument handling.
    parser = argparse.ArgumentParser(
            description='Search the package cache', version='0.1')
    parser.add_argument('-i', '--init',
            help='Initialize database', action="store_true")
    args = parser.parse_args()
    main(**vars(args))
