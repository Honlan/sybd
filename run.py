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
	return render_template('index.html')

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