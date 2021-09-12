import redis
try :
    redis = redis.StrictRedis(host ='localhost' , port = 6379 , db = 2 , password = '' , decode_responses = True)
except Exception as e:
    print(f'[-] i cant connect to the redis {str(e)}')
    exit()
redis.sadd("Main-Admins" , "1845133845")