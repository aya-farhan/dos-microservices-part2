from flask import Flask
import requests
import json
from collections import OrderedDict

app = Flask(__name__)

# in this microservice all i do is routing the coming rquest to the corresponding responsible server which run on the sam VM ith different ports (192.168.1.4:5000-->order_server, 192.168.1.4:5001-->catalog_server)

replica_index = 0  # 0-> origin, 1-> replica
cache = OrderedDict()  # ordered dict structure to implement LRU cache
cache_capacity = 3  # number of queries cache can hold and save

catalog_server_ip = "http://192.168.1.8:5001"
order_server_ip = "http://192.168.1.8:5000"
replica_catalog_server_ip = "http://192.168.1.10:5001"
replica_order_server_ip = "http://192.168.1.10:5000"


@app.route('/search/<topic>')
def search(topic):
    url = "/search/" + topic

    if url in cache:
        cache.move_to_end(url)  # to remark it as recently used
        return json.dumps(cache[url])

    global replica_index
    if replica_index == 0:
        result = requests.get(catalog_server_ip + '/search/' + topic).json()

    elif replica_index == 1:
        result = requests.get(replica_catalog_server_ip + '/search/' + topic).json()

    replica_index = 1 - replica_index

    cache[url] = result
    cache.move_to_end(url)
    if len(cache) > cache_capacity:
        cache.popitem(last=False)  # in case cache is full drop the LRU query -which is the first in the dict

    return json.dumps(result)


# to catalog_server
@app.route('/info/<book_id>')
def info(book_id):
    url = "/info/" + str(book_id)

    if url in cache:
        cache.move_to_end(url)
        return json.dumps(cache[url])

    global replica_index
    if replica_index == 0:
        result = requests.get(catalog_server_ip + '/info/' + str(book_id)).json()

    elif replica_index == 1:
        result = requests.get(replica_catalog_server_ip + '/info/' + str(book_id)).json()

    replica_index = 1 - replica_index

    cache[url] = result
    cache.move_to_end(url)
    if len(cache) > cache_capacity:
        cache.popitem(last=False)

    return result


# to order_server
@app.route('/purchase/<book_id>', methods=['POST', 'PUT'])
def purchase(book_id):
    global replica_index

    if replica_index == 0:
        result = requests.get(order_server_ip + '/purchase/' + str(book_id)).json()
    elif replica_index == 1:
        result = requests.get(replica_order_server_ip + '/purchase/' + str(book_id)).json()

    replica_index = 1 - replica_index

    return result


# when a write operation affect a cached query this fuction inalid that cache
@app.route('/invalidate/info/<book_id>', methods=['POST', 'PUT'])
def invalidate_info(book_id):
    url = "/info/" + str(book_id)

    if url in cache:
        del cache[url]

    return "success"
