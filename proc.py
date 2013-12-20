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
    for row in cur.fetchall():
        print '==================='
        iter = row.__iter__()
        print 'Package name: ' + iter.next()
        if args['hide_description'] is not '':
            print 'Description: ' + iter.next()
        if args['priority']:
            print 'Priority: ' + iter.next()

def buildOrderBy(args, cur):
    orderByClause = " ORDER BY " + args['sort=alpha'] + " " + args['asc']
    return orderByClause

def buildSelect(args, cur):
    selectClause = "SELECT package.name" + args['hide_description']
    if args['priority']:
        selectClause += ', compatibility.priority'
    if args['depend']:
        selectClause += ', compatibility.dependencies'
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
    whereClause = ' WHERE '
    if args['exact']:
        whereClause += ' package.name = %(search_term)s AND '
    if args['priority']:
        whereClause += ' compatibility.priority = %(priority)s AND '
    if args['depend']:
        whereClause += ' %(depend)s = ANY(compatibility.dependencies) AND '
    if whereClause == ' WHERE ':
        return ''
    # Trim last ' AND '.
    return whereClause[0:-5]

def buildSearchTerm(args):
    term = ''
    for w in args['search_term']:
        term += w
    args['search_term'] = term
