#!/usr/bin/env python3
import ctypes, mmap, multiprocessing as mp, os, tempfile

def child(path, barrier, queue):
    with open(path,'r+b',buffering=0) as f:
        with mmap.mmap(f.fileno(),4096,access=mmap.ACCESS_WRITE) as mm:
            addr=ctypes.addressof(ctypes.c_char.from_buffer(mm))
            queue.put((os.getpid(),hex(addr)))
            barrier.wait()
            print('Child sees:',mm[:12],flush=True)
            barrier.wait()

def main():
    with tempfile.TemporaryDirectory() as d:
        path=os.path.join(d,'shared.bin')
        with open(path,'wb') as f:f.write(b'Hello mmap!'+bytes(4096-11))
        barrier=mp.Barrier(2);queue=mp.Queue()
        proc=mp.Process(target=child,args=(path,barrier,queue));proc.start()
        with open(path,'r+b',buffering=0) as f:
            with mmap.mmap(f.fileno(),4096,access=mmap.ACCESS_WRITE) as mm:
                addr=ctypes.addressof(ctypes.c_char.from_buffer(mm))
                pid,other=queue.get(timeout=5)
                print('Parent PID/VA:',os.getpid(),hex(addr),'child PID/VA:',pid,other)
                print('Same file-backed shared mapping: yes; same PFN cannot be proven without privileged pagemap access')
                mm[:5]=b'HELLO'
                barrier.wait();barrier.wait()
        proc.join(timeout=5)
        if proc.exitcode != 0: raise RuntimeError('child failed')
if __name__=='__main__':main()
