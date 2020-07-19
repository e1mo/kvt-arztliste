from os import environ as env
from dotenv import load_dotenv
import json
import psycopg2
import csv
import argparse

load_dotenv()

rows = {}
rows['expertise'] = {}
rows['focus'] = {}
rows['designation'] = {}
rows['service'] = {}
rows['contract'] = {}

inserts = {}
inserts['service'] = []
inserts['designation'] = []
inserts['focus'] = []
inserts['contract'] = []
inserts['expertise'] = []

db_host = None
db_user = None
db_name = None
db_pass = None
skip_options = False

if "DB_HOST" in env:
    db_host = env['DB_HOST']

if "DB_NAME" in env:
    db_name = env['DB_NAME']

if "DB_USER" in env:
    db_user = env['DB_USER']

if "DB_PASS" in env:
    db_pass = env['DB_PASS']

if "SKIP_OPTIONS" in env and env['SKIP_OPTIONS'] is not False:
    skip_options = True

parser = argparse.ArgumentParser(
    description="Import select options and doctors to specified PostgreSQL Database."+
    "These files must be present in the out folder.\n" + 
    "You can define the these parameters via environment vars to or using a .env file. Refer to the documentation for details on how to use that. Refer to the documentation for details on how to use that.\n\n" +
    "This file is part of the kvt-arztliste scraper available at https://github.com/e1mo/kvt-arztliste and released under the BSD 2-Clause License. See LICENSE for the full license.")
parser.add_argument('--db-host', '-H', help='PostgreSQL Database Host', required=db_host is None)
parser.add_argument('--db-name', '-n', help='PostgreSQL Database Name', required=db_name is None)
parser.add_argument('--db-user', '-u', help='PostgreSQL Database Username', required=db_user is None)
parser.add_argument('--db-pass', '-p', help='PostgreSQL Database Password. If not defined, you will be prompted', required=False)
parser.add_argument('--skip-options', '-s', help='Don\'t import the options again', required=False, nargs='*')
args = parser.parse_args()

if args.db_host is not None:
    db_host = args.db_host

if args.db_name is not None:
    db_name = args.db_name

if args.db_user is not None:
    db_user = args.db_user

if args.db_pass is not None:
    db_pass = args.db_pass

if args.skip_options is not None:
    if args.skip_options is not False:
        skip_options = True
    else:
        skip_options = False

if db_pass is None:
    db_pass = input('Database password: ')

try:
    db = psycopg2.connect(
        user=db_user,
        password=db_pass,
        host=db_host,
        database=db_name
    )

    cursor = db.cursor()
    query = """INSERT INTO {} (num,name) VALUES {} ON CONFLICT (num) DO NOTHING"""

    with open('out/selFachgebiet.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows['expertise'][row['name']] = int(row['num'])

    with open('out/selSchwerpunkt.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows['focus'][row['name']] = int(row['num'])

    with open('out/selzusatzbezeichnung.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows['designation'][row['name']] = int(row['num'])

    with open('out/selGenehmigung.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows['service'][row['name']] = int(row['num'])

    with open('out/selSelektivvertraege.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows['contract'][row['name']] = int(row['num'])

    if not skip_options:
        for key,items in rows.items():
            tmpIn = ()
            for name,num in items.items():
                tmpIn = tmpIn + (num, name)

            cursor.execute(query.format(key, ','.join(['(%s,%s)'] * len(items))),tmpIn)

    with open('out/doctors.json') as f:
        query = """INSERT INTO doctor ({}) VALUES {} ON CONFLICT DO NOTHING RETURNING id"""
        timesQuery = """INSERT INTO doctor_time (doctor_id,day,start_at,end_at,description) VALUES {} ON CONFLICT DO NOTHING"""
        doctors = json.load(f)
        docIns = ()
        docTimes = ()
        normalParams = [
            'name', 'telephone', 'url', 'address'
        ]


        for index,doc in enumerate(doctors):
            fields = []
            for param in normalParams:
                if param in doc:
                    docIns = docIns + (doc[param],)
                else:
                    docIns = docIns + (None,)

            if 'coordinates' in doc:
                docIns += ('({},{})'.format(doc['coordinates']['lat'],doc['coordinates']['lon']),)
            else:
                docIns += '(0,0)'

        normalParams.append('coordinates')

        qry = query.format(','.join(normalParams), ','.join(['(' + ','.join(['%s'] * len(normalParams)) + ')'] * len(doctors)))
        cursor.execute(qry, docIns)
        ids = cursor.fetchall()
        

        if len(ids) > 0:
            for index,doc in enumerate(doctors):
                docid = ids[index][0]
                if 'serviceRange' in doc:
                    for service in doc['serviceRange']:
                        inserts['service'].append((docid, rows['service'][service]))

                if 'additionalDesignation' in doc:
                    for designation in doc['additionalDesignation']:
                        inserts['designation'].append((docid, rows['designation'][designation]))

                if 'specialContracts' in doc:
                    for contract in doc['specialContracts']:
                        inserts['contract'].append((docid, rows['contract'][contract]))

                if 'focus' in doc:
                    for focus in doc['focus']:
                        inserts['focus'].append((docid, rows['focus'][focus]))

                if 'field' in doc:
                    inserts['expertise'].append((docid, rows['expertise'][doc['field']]))

                if 'times' in doc:
                    for day,times in doc['times'].items():
                        for time,description in times.items():
                            _time = time.replace(' Uhr', '').split(' - ')
                            add = (docid,day,_time[0],_time[1],description)
                            docTimes = docTimes + add

            query = """INSERT INTO doctor_{0} (doctor_id, {0}_num) VALUES {1} ON CONFLICT DO NOTHING"""

            for param,items in inserts.items():
                if len(items) > 0:
                    qry = query.format(param, ','.join(['(%s,%s)'] * len(items)))
                    data = ()
                    for item in items:
                        data = data + item

                    cursor.execute(qry,data)

            qry = timesQuery.format(','.join(['(%s,%s,%s,%s,%s)'] * (int(len(docTimes) / 5))))
            cursor.execute(qry, docTimes)

    db.commit()

finally:
    if (db):
        cursor.close()
        db.close()


