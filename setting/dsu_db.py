# -*- coding: utf-8 -*-


import pymysql.cursors
import yaml
import pandas as pd
import os

cwd = os.getcwd()
path_to_ini = os.path.join(cwd, 'setting/config.yaml')

class Database(object):



    def __init__(self):

        with open(path_to_ini, "r") as stream:
            config = yaml.load(stream, Loader=yaml.Loader)

        self.conn = pymysql.connect(host=config['mysql']['host'],
                                    user=config['mysql']['user'],
                                    password=config['mysql']['password'],
                                    db=config['mysql']['database'])

    def insert(self, table, datadict):

        placeholders = ', '.join(['%({})s'.format(k) for k in datadict.keys()])
        columns = ", ".join(datadict.keys())
        all_update = ', '.join(['{key} = VALUES({key})'.format(key=k) for k in datadict.keys() ])

        sql = ("INSERT INTO {} ({}) "
               "VALUES ({}) "
               "ON DUPLICATE KEY UPDATE {}"
               ).format(table, columns, placeholders, all_update)

        with self.conn.cursor() as db_cursor:
           db_cursor.execute(sql, datadict)

        self.conn.commit()

    def get_table(self, table):

        sql = 'SELECT * FROM {}'.format(table)

        df = pd.read_sql_query(sql, self.conn)

        return df

    def query(self, sql):

        df = pd.read_sql_query(sql, self.conn)

        return df


    def close(self):
        self.conn.close()