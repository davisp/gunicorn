# -*- coding: utf-8 -
#
# This file is part of gunicorn released under the MIT license. 
# See the NOTICE for more information.

import errno
import fcntl
import os
import resource
import select
import socket
import textwrap
import time

MAXFD = 1024
if (hasattr(os, "devnull")):
   REDIRECT_TO = os.devnull
else:
   REDIRECT_TO = "/dev/null"

timeout_default = object()

CHUNK_SIZE = (16 * 1024)

MAX_BODY = 1024 * (80 + 32)

weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
monthname = [None,
             'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
             
def get_maxfd():
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = MAXFD
    return maxfd

def close_on_exec(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFD) | fcntl.FD_CLOEXEC
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)
    
def set_non_blocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK
    fcntl.fcntl(fd, fcntl.F_SETFL, flags)

def close(sock):
    try:
        sock.close()
    except socket.error:
        pass
  
def read_partial(sock, length):
    while True:
        try:
            ret = select.select([sock.fileno()], [], [], 0)
            if ret[0]: break
        except select.error, e:
            if e[0] == errno.EINTR:
                continue
            raise
    data = sock.recv(length)
    return data

def write(sock, data):
    buf = ""
    buf += data
    i = 0
    while buf:
        try:
            bytes = sock.send(buf)
            if bytes < len(buf):
                buf = buf[bytes:]
                continue
            return len(data)
        except socket.error, e:
            if e[0] in (errno.EWOULDBLOCK, errno.EAGAIN):
                break
            raise
        i += 1
        
def write_nonblock(sock, data):
    timeout = sock.gettimeout()
    if sock.gettimeout() > 0.0:
        try:
            sock.setblocking(0)
            return write(sock, data)
        finally:
            sock.setblocking(1)
    else:
        return write(sock, data)
    
def writelines(sock, lines):
    for line in list(lines):
        write(sock, line)

def write_error(sock, mesg):
    html = textwrap.dedent("""\
    <html>
        <head>
            <title>Internal Server Error</title>
        </head>
        <body>
            <h1>Internal Server Error</h1>
            <h2>WSGI Error Report:</h2>
            <pre>%s</pre>
        </body>
    </html>
    """) % mesg
    http = textwrap.dedent("""\
    HTTP/1.0 500 Internal Server Error\r
    Connection: close\r
    Content-Type: text/html\r
    Content-Length: %d\r
    \r
    %s
    """) % (len(http), http)
    write_nonblock(sock, http)

def normalize_name(name):
    return  "-".join([w.lower().capitalize() for w in name.split("-")])
    
def import_app(module):
    parts = module.rsplit(":", 1)
    if len(parts) == 1:
        module, obj = module, "application"
    else:
        module, obj = parts[0], parts[1]
    mod = __import__(module)
    parts = module.split(".")
    for p in parts[1:]:
        mod = getattr(mod, p, None)
        if mod is None:
            raise ImportError("Failed to import: %s" % module)
    app = getattr(mod, obj, None)
    if app is None:
        raise ImportError("Failed to find application object: %r" % obj)
    if not callable(app):
        raise TypeError("Application object must be callable.")
    return app

def http_date(timestamp=None):
    """Return the current date and time formatted for a message header."""
    if timestamp is None:
        timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
            weekdayname[wd],
            day, monthname[month], year,
            hh, mm, ss)
    return s
