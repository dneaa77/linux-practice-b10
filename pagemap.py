#!/usr/bin/env python3
import ctypes, os, struct
PAGE = os.sysconf('SC_PAGE_SIZE')
obj = ctypes.c_uint64(123456789)
addr = ctypes.addressof(obj)
print('PID:',os.getpid(),'virtual address:',hex(addr),'page size:',PAGE)
print('Mapping covering address:')
with open('/proc/self/maps') as f:
    for line in f:
        bounds=line.split()[0]
        a,b=(int(x,16) for x in bounds.split('-'))
        if a <= addr < b: print(line.strip());break
with open('/proc/self/pagemap','rb') as f:
    f.seek((addr//PAGE)*8)
    entry=struct.unpack('Q',f.read(8))[0]
present=bool(entry & (1<<63)); swapped=bool(entry & (1<<62)); pfn=entry & ((1<<55)-1)
print('present:',present,'swapped:',swapped,'PFN field:',pfn)
if not present: print('Page not present; no physical address available')
elif pfn==0: print('PFN hidden by kernel permissions or unavailable; root alone may not be enough (CAP_SYS_ADMIN required)')
else: print('Physical address:',hex(pfn*PAGE + addr%PAGE))
