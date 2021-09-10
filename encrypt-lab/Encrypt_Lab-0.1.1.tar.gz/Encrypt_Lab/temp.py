# import numpy as np
# from Encrypt_Lab.Sim import rand, transfer,clean_view, clean, from_binary
#
# safe_len = int(1e9)
# alice_bases = rand(safe_len)
# eav_bases = rand(safe_len)
# bob_bases = rand(safe_len)
# alice_values = rand(safe_len)
# eav_values = transfer(eav_bases,alice_bases, alice_values)
# bob_values = transfer(eav_bases, bob_bases, eav_values)
# alice_values_clean = clean_view(bob_bases,alice_bases, alice_values)
# bob_values_clean = clean_view(bob_bases, alice_bases, bob_values)
# bob_final = clean(bob_bases, alice_bases, bob_values)
# alice_final = clean(bob_bases, alice_bases, alice_values)
#
# h = {'bits count':safe_len, 'match base count':len(alice_final), 'match result count':np.count_nonzero(alice_final == bob_final), 'missmatch result count':np.count_nonzero(alice_final != bob_final)}
# h['missmatch ratio'] = h['missmatch result count']/ h['match base count']
#
#
#
# print(h)
#
#
import numpy as np
num = int(1e5)
print(np.sqrt(num*0.75*0.25))
print(np.std([np.count_nonzero(np.random.randint(4, size=num, dtype=int) ==3) for a in range(1000000)]))



