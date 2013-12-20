import psycopg2, argparse, apt, sys

def processQuery(args, cur):
    selectClause = buildSelect(args, cur)
    whereClause = buildWhere(args, cur)
    orderByClause = buildOrderBy(args, cur)
    fromClause = buildFrom(selectClause, whereClause, args, cur)
    print selectClause + fromClause + whereClause + orderByClause
    buildSearchTerm(args)
    cur.execute(selectClause + fromClause + whereClause + orderByClause,
                args)
    print(cur.fetchall())

def buildOrderBy(args, cur):
    orderByClause = " ORDER BY " + args['sort=alpha'] + " " + args['asc']
    return orderByClause

def buildSelect(args, cur):
    selectClause = "SELECT package.name" + args['hide_description']
    return selectClause

def buildFrom(select, where, args, cur):
    fromClause = ' FROM package '
    for tn in ['fileinfo',
        'descriptor', 'compatibility',
        'maintains', 'maintainer']:
        if tn in select + where:
            fromClause += ' NATURAL JOIN ' + tn + ' '
    return fromClause

def buildWhere(args, cur):
    if args['exact']:
        whereClause = ' WHERE package.name = %(search_term)s'
        return whereClause
    return ''

def buildSearchTerm(args):
    term = ''
    for w in args['search_term']:
        term += w
    args['search_term'] = term
