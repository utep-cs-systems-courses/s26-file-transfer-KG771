#! /usr/bin/env python3

# Echo server program

import socket, sys, re, time, os
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )



progname = "server"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''       # Symbolic name meaning all available interfaces

pidAddr = {}  #for active connections: maps pid -> client addr

if paramMap['usage']:
    params.usage()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f"server listening at ip addr {listenAddr} port #{listenPort}")
s.bind((listenAddr, listenPort))
s.listen(1)              # allow only one outstanding request
# s is a factory for connected sockets

while True:
    # reap zombie children (if any)
    while pidAddr.keys():
        # Check for exited children (zombies).  If none, don't block (hang)
        if (waitResult := os.waitid(os.P_ALL, 0, os.WNOHANG | os.WEXITED)): 
            zPid, zStatus = waitResult.si_pid, waitResult.si_status
            print(f"""zombie reaped:
            \tpid={zPid}, status={zStatus}
            \twas connected to {pidAddr[zPid]}""")
            del pidAddr[zPid]
        else:
            break               # no zombies; break from loop
    print(f"Currently {len(pidAddr.keys())} clients")

    try:
        connSockAddr = listenSock.accept() # accept connection from a new client
    except TimeoutError:
        connSockAddr = None 

    if connSockAddr is None:
        continue
        
    forkResult = os.fork()     # fork child for this client 
    if (forkResult == 0):        # child
        listenSock.close()         # child doesn't need listenSock
        chatWithClient(connSockAddr)
    # parent
    sock, addr = connSockAddr
    sock.close()   # parent closes its connection to client
    pidAddr[forkResult] = addr
    print(f"spawned off child with pid = {forkResult} at addr {addr}")

