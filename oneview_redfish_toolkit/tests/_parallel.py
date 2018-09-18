#!/usr/bin/python3
import json
import logging
import logging.config
import ssl
from threading import Thread
from random import randint
import time
import urllib3

urllib3.disable_warnings()
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.basicConfig(filename='results.log', level=logging.INFO)

REDFISH_IP = 'blso-redfish-server-01.vse.rdlabs.hpecorp.net'
#REQ_URL = '/redfish/'
REQ_URL = '/redfish/v1/CompositionService/ResourceBlocks/197a62e4-f2c7-4097-a098-9ade31a4a353/Storage/1'
#REQ_URL = '/redfish/v1/CompositionService/ResourceBlocks/197a62e4-f2c7-4097-a098-9ade31a4a353'
#REQ_URL = ['/redfish/v1/CompositionService/ResourceZones/13d6739e-2856-4744-8a10-63ccbda0268e-0000000000A66101',
#'/redfish/v1/CompositionService/ResourceBlocks/197a62e4-f2c7-4097-a098-9ade31a4a353',
#'/redfish/v1/CompositionService/ResourceBlocks/197a62e4-f2c7-4097-a098-9ade31a4a353/Storage/1',
#'/redfish/v1/CompositionService/ResourceBlocks/30303437-3034-4D32-3230-313130304752',
#'/redfish/v1/CompositionService/ResourceBlocks/30303437-3034-4D32-3230-313130304752/Systems/1',
#'/redfish/v1/CompositionService/ResourceBlocks/30303437-3034-4D32-3230-313130304752/Systems/1/Processors',
#'/redfish/v1/CompositionService/ResourceBlocks/30303437-3034-4D32-3230-313130304752/Systems/1/Processors/1',
#'/redfish/v1/CompositionService/ResourceBlocks/13d6739e-2856-4744-8a10-63ccbda0268e',
#'/redfish/v1/CompositionService/ResourceBlocks/13d6739e-2856-4744-8a10-63ccbda0268e/EthernetInterfaces/1']

N_REQ_PER_THREAD = 100

#http = urllib3.HTTPSConnectionPool(REDFISH_IP, 5000, cert_reqs='CERT_NONE')

def function_to_run():
    http = urllib3.HTTPSConnectionPool(REDFISH_IP, 5000, cert_reqs='CERT_NONE')
    for i in range(N_REQ_PER_THREAD):
        resp = http.request('GET', REQ_URL)
        #resp = http.request('GET', REQ_URL[randint(0,8)])
        if resp.status != 200:
            logging.info(resp.data)

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
    logging.info('Starting tests')

    for n_threads in range(2, 150, 5):
        start_time = time.time()
        threaded(n_threads)
        end_time = time.time()
        total_time = (end_time - start_time) / N_REQ_PER_THREAD

        logging.info("Threads {} : {}".format(n_threads, total_time))

    logging.info('Iterations complete')
