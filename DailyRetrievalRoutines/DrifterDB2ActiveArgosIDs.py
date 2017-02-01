#!/usr/bin/env python

"""
DrifterDB2ActiveArgosIDs.py

Outputs to Standard Out (Screen) Argos IDs listed as active in the EcoFOCI Argos Drifter Database
for use with the ArgosDrifters2KML visualization routine
 
Using Anaconda packaged Python 
"""
#System Stack
import argparse
import pymysql

#user stack
import utilities.ConfigParserLocal as ConfigParserLocal

"""--------------------------------SQL Init----------------------------------------"""

def connect_to_DB(host, user, password, database):
    # Open database connection
    try:
        db = pymysql.connect(host, user, password, database)
    except:
        print "db error"
        
    # prepare a cursor object using cursor() method
    cursor = db.cursor(pymysql.cursors.DictCursor)
    return(db,cursor)

def read_db(db, cursor, table, IsActive='Y'):
    sql = ("SELECT * from `{0}` WHERE `IsActive`= '{1}'").format(table, IsActive)

    result_dic = {}
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # Get column names
        rowid = {}
        counter = 0
        for i in cursor.description:
            rowid[i[0]] = counter
            counter = counter +1 
        #print rowid
        # Fetch all the rows in a list of lists.
        results = cursor.fetchall()
        for row in results:
            result_dic[row['id']] ={keys: row[keys] for val, keys in enumerate(row.keys())} 
        return (result_dic)
    except:
        print "Error: unable to fecth data"


def close_DB(db):
    # disconnect from server
    db.close()
    
"""------------------------------------- Main -----------------------------------------"""

# parse incoming command line options
parser = argparse.ArgumentParser(description='Create ActiveArgosIDs text file')
parser.add_argument('db_ini', metavar='db_ini', type=str, help='full path to db_config.pyini file')

args = parser.parse_args()

db_config = ConfigParserLocal.get_config(args.db_ini)
(db,cursor) = connect_to_DB(db_config['host'], db_config['user'], db_config['password'], db_config['database'])
table = 'drifter_ids'
data = read_db(db, cursor, table)
close_DB(db)

for k,v in enumerate(data):
    print data[v]['ArgosNumber']