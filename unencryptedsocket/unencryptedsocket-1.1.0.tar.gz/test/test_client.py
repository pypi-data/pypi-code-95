from unencryptedsocket import *
import threading


ps = []
for i in range(100):
    def job(i):
        print(SC().request(command="test_command", data=args("Hello, {}!".format(i))))
    p = threading.Thread(target=job, args=(i,))
    ps.append(p)
    p.start()
for p in ps:
    p.join()

# will fail running in parallel
sc = SC()
# best to use template like:
# sc = lambda: SC(host=..., port=...)
# response = sc().request(...)
long_data = "Hello, 999!"*999
response = sc.request(command="test_command", data=args(long_data))
print(response, len(long_data))
sc.s.close()
print("test socket client started.", flush=True)
