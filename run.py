#!/usr/bin/env python
# coding:utf8

import time
import sys
reload(sys)
sys.setdefaultencoding( "utf8" )
from flask import *
import warnings
warnings.filterwarnings("ignore")
import MySQLdb
import MySQLdb.cursors
import numpy as np
from config import *
import pprint
import random
import json

app = Flask(__name__)
app.config.from_object(__name__)

# 连接数据库
def connectdb():
	db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWORD, db=DATABASE, port=PORT, charset=CHARSET, cursorclass = MySQLdb.cursors.DictCursor)
	db.autocommit(True)
	cursor = db.cursor()
	return (db,cursor)

# 关闭数据库
def closedb(db,cursor):
	db.close()
	cursor.close()

# 首页
@app.route('/')
def index():
	dataset = {}

	(db,cursor) = connectdb()

	cursor.execute("select * from json_data where page=%s", ['index'])
	
	json_data = cursor.fetchall()
	tmp = {}
	for item in json_data:
		tmp[item['keyword']] = json.loads(item['json'])
	dataset['json'] = tmp

	closedb(db,cursor)

	hour = str(((int(time.time()) % (3600 * 24)) / 3600 + 8) % 24)
	dataset['json']['human']['hour'] = hour
	timestamp = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
	for key in dataset['json']['human']['bar'].keys():
		dataset['json']['human']['bar'][key] = [int(dataset['json']['human']['bar'][key][t][0] / float(dataset['json']['human']['bar'][key][t][1])) for t in timestamp]

	for key in dataset['json']['human']['tree'].keys():
		for p in dataset['json']['human']['tree'][key].keys():
			for sp in dataset['json']['human']['tree'][key][p].keys():
				dataset['json']['human']['tree'][key][p][sp] = int(dataset['json']['human']['tree'][key][p][sp][0] / dataset['json']['human']['tree'][key][p][sp][1])

	for t in dataset['json']['human']['tree'].keys():
		tmp = []
		for p in dataset['json']['human']['tree'][t].keys():
			pvalue = 0
			children = []
			for sp in dataset['json']['human']['tree'][t][p].keys():
				children.append({
					'name': sp,
					'path': p + '/' + sp,
					'value': dataset['json']['human']['tree'][t][p][sp]
					})
				pvalue += dataset['json']['human']['tree'][t][p][sp]
			tmp.append({
				'name': p,
				'path': p,
				'value': pvalue,
				'children': children
				})
		dataset['json']['human']['tree'][t] = tmp
	
	return render_template('index.html', dataset=json.dumps(dataset))

# 宏观
@app.route('/macro')
def macro():
	dataset = {}

	(db,cursor) = connectdb()

	cursor.execute("select * from json_data where page=%s", ['macro'])
	
	json_data = cursor.fetchall()
	tmp = {}
	for item in json_data:
		tmp[item['keyword']] = json.loads(item['json'])
	dataset['json'] = tmp

	tmp = []
	for item in dataset['json']['bus_lines']:
		if len(item['stations']):
			tmp.append({"coords": [[i[1], i[2]] for i in item['stations']]})
	dataset['json']['bus_lines'] = tmp

	closedb(db,cursor)
	
	return render_template('macro.html', dataset=json.dumps(dataset))

# 微观
@app.route('/micro')
def micro():
	return render_template('micro.html')

# 介观
@app.route('/meso')
def meso():
	return render_template('meso.html')

if __name__ == '__main__':
	app.run(debug=True)