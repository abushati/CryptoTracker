from redis import Redis


#Todo: Turn this into a class

#This would be in the init function. look at redis handle for o365_onedrive
def redis():
    # return Redis(host='127.0.0.1', port=6379)
    return Redis(host= 'cryptotracker_redis', port=6379)
