import json


a = [1, 2, 3, 4, 5]
print(type(a), a)
a_str = json.dumps(a)

print(type(a_str), a_str)

a_reborn = json.loads(a_str)


print(type(a_reborn), a_reborn)
