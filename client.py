#! /usr/bin/env python3

# Echo client program
import socket, sys, re, os
sys.path.append("../lib")       # for params
import params

switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, filename, usage = paramMap["server"], paramMap["filename"], paramMap["usage"]
 
if usage:
    params.usage()
 
try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)
 
# --- Connect to server ---
 
s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print("Creating socket: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print("  Error: %s" % msg)
        s = None
        continue
    try:
        print("  Connecting to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print("  Error: %s" % msg)
        s.close()
        s = None
        continue
    break
 
if s is None:
    print("Could not open socket")
    sys.exit(1)
 
# --- Request a file from the server ---
 
print(f"Requesting file: '{filename}'")
framing.send_frame(s, filename)
 
# Receive status (OK or ERROR message)
response = framing.recv_frame(s)
if not response:
    print("Server closed connection unexpectedly")
    s.close()
    sys.exit(1)
 
status = response.decode()
 
if status.startswith("ERROR"):
    print(f"Server responded: {status}")
    s.close()
    sys.exit(1)
 
# Status was OK — receive the file contents
file_data = framing.recv_frame(s)
if not file_data:
    print("Server closed connection before sending file data")
    s.close()
    sys.exit(1)
 
print(f"Received {len(file_data)} bytes")
print("--- File contents ---")
print(file_data.decode(errors='replace'))
print("--- End of file ---")
 
s.close()
print("Done.")
 