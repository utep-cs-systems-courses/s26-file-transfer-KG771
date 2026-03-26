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

def chatWithClient(connAddr):
    sock, addr = connAddr
    print(f"Child pid={os.getpid()} connected to {addr}")
 
    try:
        # Receive the requested filename
        request = framing.recv_frame(sock)
        if not request:
            print("Client disconnected before sending filename")
            sock.close()
            sys.exit(1)
 
        filename = request.decode()
        print(f"Client requests file: '{filename}'")
 
        # Try to open and send the file
        try:
            with open(filename, 'rb') as f:
                file_data = f.read()
            framing.send_frame(sock, b"OK")
            framing.send_frame(sock, file_data)
            print(f"Sent {len(file_data)} bytes for '{filename}'")
        except FileNotFoundError:
            error_msg = f"ERROR: File '{filename}' not found"
            print(error_msg)
            framing.send_frame(sock, error_msg.encode())
 
    except Exception as e:
        print(f"Error in child: {e}")
    finally:
        sock.close()
 
    sys.exit(0)   # child must exit here — do not fall through into parent loop
 
# --- Set up listening socket ---
 
listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listenSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # rebind immediately after crash
listenSock.settimeout(5)          # accept() blocks at most 5s so we can reap zombies
listenSock.bind((listenAddr, listenPort))
listenSock.listen(5)              # backlog of 5 pending connections
 
print(f"Server listening on port {listenPort}")
 
# --- Main accept loop ---
 
while True:
    # Reap any zombie children
    while pidAddr.keys():
        if (waitResult := os.waitid(os.P_ALL, 0, os.WNOHANG | os.WEXITED)):
            zPid, zStatus = waitResult.si_pid, waitResult.si_status
            print(f"Zombie reaped: pid={zPid}, status={zStatus}, was connected to {pidAddr[zPid]}")
            del pidAddr[zPid]
        else:
            break   # no more zombies right now
 
    print(f"Currently {len(pidAddr)} active client(s)")
 
    try:
        connSockAddr = listenSock.accept()
    except TimeoutError:
        connSockAddr = None
 
    if connSockAddr is None:
        continue
 
    forkResult = os.fork()
    if forkResult == 0:            # child process
        listenSock.close()         # child doesn't need the listening socket
        chatWithClient(connSockAddr)
        # chatWithClient calls sys.exit(0), so we never reach here
 
    # Parent process
    sock, addr = connSockAddr
    sock.close()                   # parent closes its copy of the connected socket
    pidAddr[forkResult] = addr
    print(f"Spawned child pid={forkResult} for client {addr}")