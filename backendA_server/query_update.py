from flask import Flask, jsonify
import sqlite3
import json
app = Flask(__name__)

#this micro service manipulate db thorough put method and query db using get, using this microservice we can query, ask for info and update 

#this function o establish db-sqlite3 connection 
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#this function to serialize data to json
def serialize_search(posts):
    list_json=[]
    for post in posts:
        list_json.append({"item number":post['id'], "title":post['name'] })
        
    return list_json
    
# --------------------------------------------------------------------------#
@app.route('/search/<topic>')
def search(topic):
    conn = get_db_connection()
    cur = conn.cursor()
    posts = cur.execute('SELECT * FROM books where topic=?', [topic]).fetchall()
    conn.close()  
      	
    if len(posts) > 0:
    	json_list = serialize_search(posts)
    	return json.dumps({"result -from origin":json_list})

    else:
        return jsonify({"result -from origin":"make sure you enter a valid topic"})
    



# --------------------------------------------------------------------------#
@app.route('/info/<book_id>')
def info(book_id):
    conn = get_db_connection()
    cur = conn.cursor()
    post = cur.execute('SELECT * FROM books where id=?', [book_id]).fetchone()
    conn.close()   
     
    if post is not None:
        return jsonify(({"result -from origin":{"item number": post['id'], "title": post['name'], "topic": post['topic'],
                     "price": post['cost'], "left in stock":post['number_of_items']}}))
    else:
        return jsonify({"result -from origin":"make sure you enter a valid book id"})


# --------------------------------------------------------------------------#
@app.route('/update/<book_id>/price/<price>', methods=['PUT', 'GET'])
def update_price(book_id, price):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE books set cost= ? where id=?', [price, book_id])
    conn.commit()
    conn.close()

    return jsonify({'result': 'success'})


# --------------------------------------------------------------------------#
@app.route('/update/<book_id>/amount_of_items/<amount>', methods=['PUT', 'GET'])
def update_amount(book_id, amount):
    conn = get_db_connection()
    cur = conn.cursor()
    result = cur.execute('select number_of_items from books where id=?', [book_id]).fetchone()
    current_amount = result['number_of_items']
    cur.execute('UPDATE books set number_of_items= ? where id=?', [current_amount + int(amount), book_id])
    conn.commit()
    conn.close()
    return jsonify({'result': 'success'})


# --------------------------------------------------------------------------#
@app.route('/query/<book_id>')
def query_book(book_id):
    print(book_id)
    conn = get_db_connection()
    cur = conn.cursor()
    post = cur.execute('SELECT * FROM books where id=?', [book_id]).fetchone()
    conn.close()
    _left = True
    if post['number_of_items'] <= 0:
        _left = False

    else:
        _left = True

    return jsonify({'result': _left})
    

