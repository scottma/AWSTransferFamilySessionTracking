import os
import json
import base64
import gzip
import time
import uuid
import sys
import socket
import elasticache_auto_discovery
from pymemcache.client.hash import HashClient

elasticache_config_endpoint = "{}:{}".format(os.environ["ElastiCacheEndpoint"], os.environ["ElastiCacheEndpointPort"])
nodes = elasticache_auto_discovery.discover(elasticache_config_endpoint)
nodes = map(lambda x: (x[1], int(x[2])), nodes)
memcache_client = HashClient(nodes)

def lambda_handler(event, context):
    # decode the payload
    compressed_payload = base64.b64decode(event['awslogs']['data'])
    uncompressed_payload = gzip.decompress(compressed_payload)
    log_payload = json.loads(uncompressed_payload)

    # process each log, logs can be combined.
    for log in log_payload['logEvents']:   
        print(log)
        parsed = log['message'].split(" ")
        user_session = parsed[0]
        user = user_session.split(".")[0]
        action = parsed[1]

        val = memcache_client.get(user)

        # # use DISCONNECTED as keyword
            if action == "DISCONNECTED":
                print("decr")
                memcache_client.decr(user,1)
            
            # this will have at value for this user by now.
            val = memcache_client.get(user).decode('utf-8')
            print( user, action, "Connection Count", val)        
    
    return {
        'statusCode': 200,
        'body': json.dumps('OK')
    }
