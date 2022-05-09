from flask import Flask, jsonify
import sqlite3
import json
import requests
import datetime

app = Flask(__name__)

#this micro service responsibility is to maintain purchases and deliver them if items are found by quering catalog_server

catalog_server_ip = "http://192.168.1.8:5001"
replica_catalog_server_ip = "http://192.168.1.10:5001"
front_server_ip = "http://192.168.1.4:5000"

#this function o establish db-sqlite3 connection 
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
    

def add_order_to_db(book_id):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    sqlite_insert_query_0 = """INSERT INTO orders
                          (book_id) 
                           VALUES 
                          ("""+str(book_id)+""")"""    
    cur.execute(sqlite_insert_query_0)
    conn.commit()
    conn.close()
    
    
@app.route('/purchase/<book_id>')
def index(book_id):
    order_completed=False
    #first check catalog server to see if book is in store
    is_available = requests.get(catalog_server_ip+'/query/'+str(book_id)).json()
    
    #if there's a book/s server presents the purchase so it update the info of this book in catalog db by decreasing its amount
    if is_available['result']:
        update_query = requests.put(catalog_server_ip+'/update/'+str(book_id)+'/amount_of_items/'+str(-1))
        if(update_query.status_code==200):
            order_completed=True
            # to satisfy the consistency requirement
            requests.put(replica_catalog_server_ip+'/update/'+str(book_id)+'/amount_of_items/'+str(-1))
            add_order_to_db(book_id)
            # invlidate an item from cache when a purchase occures because its info and data changed  
            requests.put(front_server_ip+'/invalidate/info/'+str(book_id))
            
            return jsonify({'result':'your purchase done successfully -from original server'})

        else:
            order_completed=False
            add_order_to_db(book_id)
            return jsonify({'result':'try again later -from original server'})

        
    else:
        order_completed=False
        add_order_to_db(book_id)
        return jsonify({'reulst -from original server':'this book is no longer available in the store'})         

