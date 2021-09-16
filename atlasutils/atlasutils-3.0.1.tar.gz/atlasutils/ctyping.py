import os
import re
import ctypes
import struct

'''
How to Read from Arbitrary Addresses:
    dllapi = ctypes.CDLL(r'C:\something.dll')
    fnptr = ctypes.cast(dllapi.SomeKnownFunction, ctypes.c_void_p).value 
    baseptr = fnptr - <FUNC_OFFSET>

How to Execute Arbitrary Functions by Address:

    dllapi = ctypes.CDLL(r'C:\something.dll')
    fnptr = ctypes.cast(dllapi.SomeKnownFunction, ctypes.c_void_p).value

    functype = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p)
    func = functype(fnptr + <OffsetToCodeToExecute>)

# some bits of code stolen from: https://gist.github.com/fxthomas/3c915909bbf84bc14782cb6adef0f915
'''

lefmts = (None, 'B', '<H', None, '<I', None, None, None, '<Q')
Befmts = (None, 'B', '>H', None, '>I', None, None, None, '>Q')
fmts = (lefmts, Befmts)

def writeMem(va, data):
    if os.name in ('nt', 'winnt', 'win32'):
        return ctypes.cdll.msvcrt.memcpy(va, data, len(data))

    return ctypes.CDLL('libc.so.6').libc.memcpy(va, data, len(data))

def writeMemValue(va, vals, fmt='<I'):
    size = struct.calcsize(fmt)
    if not type(vals) in (list, tuple):
        # make it a list/tuple
        vals = [vals]
    #print("writing (fmt: %r) %r to 0x%x" % (fmt, vals, va))
    data = struct.pack(fmt, *vals)
    return writeMem(va, data)

def writeMemPtr(va, vals, psize=4, bigend=False):
    fmt = fmts[bigend][psize]
    return writeMemValue(va, vals, fmt)


def readMem(va, size=4):
    return ctypes.string_at(va, size)

def readMemValue(va, fmt='<I'):
    size = struct.calcsize(fmt)
    inpstr = readMem(va, size)
    return struct.unpack(fmt, inpstr)

def readMemPtr(va, psize=4, bigend=False):
    fmt = fmts[bigend][psize]
    return readMemValue(va, fmt)[0]

def searchMem(baseva, size, pattern=b'hellosearch', blocksize=0x1000):
    endva = baseva + size
    searchlen = len(pattern)
    for offset in range(0, size, blocksize):
        try:
            va = baseva + offset
            readsz = blocksize + searchlen  # search for one more of the pattern...
            leftoversz = endva - va
            readsz = min(readsz, leftoversz)
            block = readMem(va, readsz)

            if pattern in block:
                pva = block.find(pattern) + va
                return pva, block
        except Exception as e:
            print("Error: %r" % e)

MAPS_LINE_RE = re.compile(r"""
    (?P<addr_start>[0-9a-f]+)-(?P<addr_end>[0-9a-f]+)\s+  # Address
    (?P<perms>\S+)\s+                                     # Permissions
    (?P<offset>[0-9a-f]+)\s+                              # Map offset
    (?P<dev>\S+)\s+                                       # Device node
    (?P<inode>\d+)\s+                                     # Inode
    (?P<pathname>.*)\s+                                   # Pathname
""", re.VERBOSE)

def findMaps(bs=0x1000):
    '''
    On Windows: Search through valid memory space looking for mapped pages
    On Linux this approach currently segfaults, so we parse /proc/self/maps

    Note: on Windows, we don't have a map name, so we include the first hand-
    full of bytes in the map.  On linux, we have map names, so we use that as
    the last field of each map in the list.
    '''
    maps = []
    if os.name == 'win32':
        # scour through memory space looking for good memory pages
        lastgood = False
        for baseva in range(0, 0xfffff000, bs):
            try:
                blockstub = readMem(baseva, 10)
                if not lastgood:
                    maps.append([baseva, 0, 0, blockstub, ''])

                lastgood = True
            except Exception as e:
                lastgood = False
                if len(maps):
                    lastmap = maps[-1]
                    if lastmap[1] == 0:
                        lastmap[1] = baseva  # tag the end of the map
                        lastmap[2] = baseva - lastmap[0] # tag the end of the map

                if 'access violation' in repr(e):
                    continue
                import traceback
                traceback.print_exc()
    elif os.name == 'posix':
        # parse /proc/self/maps
        with open("/proc/self/maps") as fd:
            for line in fd:
                m = MAPS_LINE_RE.match(line)
                if not m:
                    print("Skipping: %s" % line)
                    continue
                addr_start, addr_end, perms, offset, dev, inode, pathname = m.groups()
                addr_start = int(addr_start, 16)
                addr_end = int(addr_end, 16)
                offset = int(offset, 16)

                # skip if we can't read...
                if 'r' not in perms:
                    continue

                #print("reading from %r (perms: %r)" % (pathname, perms))
                fprint = readMem(addr_start, 10)
                #fprint = ''
                maps.append((
                    addr_start,
                    addr_end,
                    addr_end - addr_start,
                    fprint,
                    pathname,
                ))

    return maps

def searchMaps(pattern=b'hellosearch', skip_bins=True, findfirst=True, maps=None, bs=0x1000):
    if maps is None:
        maps = findMaps()

    findings = []

    for mapva, mapend, mapsz, fprint, pathname in maps:
        try:
            if skip_bins:
                if fprint.startswith(b'MZ') or fprint.startswith(b'\x7ELF') or fprint.startswith(b'Actx'):
                    continue

            block = readMem(mapva, mapsz)

            if pattern in block:
                print("pattern found in block 0x%x" % mapva)
                off = block.find(pattern)

                while off != -1:
                    pva = mapva + off
                    findings.append((pva))

                    if findfirst:
                        return pva

                    off = block.find(pattern, off+1)

        except Exception as e:
            print("Error: %r" % e)

    return findings

def dumpFindings(findings):
    for va in findings:
        print("0x%x: %r" % (va, readMem(va, 100)))

PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_NOACCESS = 1
PAGE_READONLY = 2
PAGE_READWRITE = 4
PAGE_WRITECOPY = 8


def VirtualProtect(addr, size, prot=PAGE_EXECUTE_READWRITE):
    oldprot = ctypes.c_uint32(0)
    retval = ctypes.windll.kernel32.VirtualProtect(addr, size, prot, ctypes.byref(oldprot))
    return retval, oldprot

def HookGOT(addr, pyfunc, ctypeargs=(), psize=4, bigend=False):
    c_callback = ctypes.CFUNCTYPE(*ctypeargs)(pyfunc)
    fmt = fmts[bigend][psize]
    return writeMemPtr(addr, struct.unpack(fmt, c_callback)[0])

