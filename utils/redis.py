from redis import Redis

def redis():
    return Redis(host='127.0.0.1', port=6379)