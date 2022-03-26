import os
from redis import Redis


#Todo: Turn this into a class

#This would be in the init function. look at redis handle for o365_onedrive
def redis():
    """
    https://docs.docker.com/compose/networking/
    For container to container communication the container port is used Ex in docker file <host_port>:<container_port>
    db:
        image: postgres
        ports:
            - "8001:5432"

    It is important to note the distinction between HOST_PORT and CONTAINER_PORT. In the above example, for db,
    the HOST_PORT is 8001 and the container port is 5432 (postgres default). Networked service-to-service communication
    uses the CONTAINER_PORT. When HOST_PORT is defined, the service is accessible outside the swarm as well.

    Within the web container, your connection string to db would look like postgres://db:5432, and from the host machine,
    the connection string would look like postgres://{DOCKER_IP}:8001.
    """
    mode = os.environ.get('MODE')
    if mode == 'PROD':
        host = 'cache'
        port = 6360
    else:
        host = '127.0.0.1'
        port = 6379
    return Redis(host=host, port=port)

def generate_alert_queue():
    mode = os.environ.get('MODE')
    if mode == 'PROD':
        host = 'generate_alert_queue'
        port = 6361
    else:
        host = '127.0.0.1'
        port = 6378
    return Redis(host=host, port=port)