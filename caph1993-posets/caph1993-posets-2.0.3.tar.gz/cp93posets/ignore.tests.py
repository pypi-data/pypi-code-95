from poset import Poset

P1 = Poset.from_parents([[1, 2], [], [], [1]])
P1.show()

P2 = Poset.from_parents([[1], [], [1, 3], []])
P2.show()

print(P1 == P2)
print(P1)
print(P2)

L1 = P1.meta_O
L1.show()