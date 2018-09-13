import json
import logging
import logging.config
import ssl
from threading import Thread
import time
import urllib3

urllib3.disable_warnings()

REDFISH_IP = 'redfish-server.net'
REQ_URL = '/redfish/v1/CompositionService/ResourceBlocks/197a62e4-f2c7-4097-a098-9ade31a4a353/Storage/1'

http = urllib3.HTTPSConnectionPool(REDFISH_IP, 5000, cert_reqs='CERT_NONE')

def function_to_run():
#    http = urllib3.HTTPSConnectionPool(REDFISH_IP, 5000, cert_reqs='CERT_NONE')

    resp = http.request('GET', REQ_URL)

#    if resp.status != 200:
#        print(resp.data)

    pass

class threads_object(Thread):
    def run(self):
        function_to_run()


def threaded(num_threads):
    funcs = []
    for i in range(int(num_threads)):
        funcs.append(threads_object())
    for i in funcs:
        i.start()
    for i in funcs:
        i.join()

def show_results(func_name, results):
    msg = "{} {} seconds".format(func_name, results)
    print(msg)

if __name__ == '__main__':

    repeat_list = [1, 3, 4, 5, 6, 7]

    print('Starting tests')

    for repeat in range(2, 150, 2):
        start_thread = time.time()
        threaded(repeat)
        print("Threads {} : {}".format(repeat, (time.time() - start_thread)))
        time.sleep(3)


    print('Iterations complete')