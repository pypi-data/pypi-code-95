rfile = open('gaff2.dat', 'r')

Flag = False
lj_section = []
for line in rfile:
    line = line.strip()
    if Flag and line.startswith('END'):
        break

    if Flag and len(line) > 0:
        lj_section.append(line)

    if line.startswith('MOD4'):
        Flag = True


print(Flag)
print(len(lj_section))
