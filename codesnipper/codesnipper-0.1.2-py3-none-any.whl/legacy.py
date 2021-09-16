COMMENT = '"""'


def gcoms(s):
    coms = []
    while True:
        i = s.find(COMMENT)
        if i >= 0:
            j = s.find(COMMENT, i+len(COMMENT))+3
        else:
            break
        if j < 0:
            raise Exception("comment tag not closed")
        coms.append(s[i:j])
        s = s[:i] + s[j:]
        if len(coms) > 10:
            print("long comments in file", i)
    return coms, s


def block_process(lines, tag, block_fun):
    i = 0
    didfind = False
    lines2 = []
    block_out = []
    cutout = []
    while i < len(lines):
        l = lines[i]
        dx = l.find(tag)
        if dx >= 0:
            if l.find(tag, dx+1) > 0:
                j = i
            else:
                for j in range(i + 1, 10000):
                    if j >= len(lines):
                        print("\n".join(lines))
                        print("very bad end-line j while fixing tag", tag)
                        raise Exception("Bad line while fixing", tag)
                    if lines[j].find(tag) >= 0:
                        break

            pbody = lines[i:j+1]
            if i == j:
                start_extra = lines[j][dx:lines[j].rfind(tag)].strip()
                end_extra = lines[j][lines[j].rfind(tag) + len(tag):].strip()
            else:
                start_extra = lines[i][dx:].strip()
                end_extra = lines[j][lines[j].rfind(tag) + len(tag):].strip()

            cutout.append(pbody)
            tmp_ = start_extra.split("=")
            arg = None if len(tmp_) <= 1 else tmp_[1].split(" ")[0]
            start_extra = ' '.join(start_extra.split(" ")[1:] )

            pbody[0] = pbody[0][:dx]
            if j > i:
                pbody[-1] = pbody[-1][:pbody[-1].find(tag)]

            nlines, extra = block_fun(lines=pbody, start_extra=start_extra, end_extra=end_extra, art=arg, head=lines[:i], tail=lines[j+1:])
            lines2 += nlines
            block_out.append(extra)
            i = j+1
            didfind = True
            if "!b" in end_extra:
                assert(False)
        else:
            lines2.append(l)
            i += 1

    return lines2, didfind, block_out, cutout