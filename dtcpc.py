#!/usr/bin/env python
# encoding: utf-8

# Referenced: http://www.gcd.org/sengoku/docs/IPv6_DTCP.html

from hashlib import md5
from poplib import POP3
import logging
FORMAT = "%(asctime)-15s : %(message)s"
logging.basicConfig(format=FORMAT,filename='/config/scripts/dtcpc.log',level=logging.DEBUG,datefmt='%Y-%m-%d %H:%M:%S')
import sys
FILENAME = sys.argv[0]

import socket

class NeedsAuthException(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class AuthFailException(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class NoConnectionException(Exception):
    def __init__(self,msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class DTCPC(POP3):

    def __init__(self,host,port,username,password,tun_type,timeout=5000.0,debug_level=5):
        self.set_debuglevel(debug_level)
        logging.info(FILENAME + ": Connecting %s:%s" % (host,port))
        POP3.__init__(self, host, port, timeout=timeout)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.username = username
        self.password = password
        self.tun_type=tun_type
        self._local = None
        self._remote = None
        self._ipv6 = None

    def _getChallenge(self):
        """
    '+OK c361f05a29f4816ce06d2d2203c13cc4 FBDC TunnelBroker (version 0.2) Ready. <870363>:4096'
        """
        welcome = self.getwelcome()
        logging.info(FILENAME + ": %s" % welcome)
        if not welcome.startswith("+OK"):
            raise NoConnectionException("can't get Challenge value")
        texts = welcome.lstrip("+OK ")
        challenge = texts[:texts.index(" ")]
        return challenge

    def _getAuthCommand(self):
        """
        tunnel sengoku f0e130bfddaef3a5a526f77738bc91a3 network
        """
        challenge = self._getChallenge()
        resp_hash = md5(self.username + challenge + self.password).hexdigest()
        resp = []
        resp.append("tunnel")
        resp.append(self.username)
        resp.append(resp_hash)
        resp.append(self.tun_type)
        command = " ".join(resp)
        return command

    def auth(self):
        """
        +OK 60.32.85.217 43.244.255.37 2001:03e0:03c3::/48
        """
        command = self._getAuthCommand()
        logging.info(FILENAME + ": %s" % command)
        self.sock.send(command + "\n")
        ret = self.sock.recv(1024)
        if not ret.startswith("+OK "):
            raise AuthFailException(ret)
        logging.info(FILENAME + ": %s" % ret)
        values = ret.split(" ")
        self._local = values[1]
        self._remote = values[2]
        self._ipv6 = values[3].strip()
        logging.info(FILENAME + ":LOCAL IP %s" % self._local)
        logging.info(FILENAME + ":REMOTE IP %s" % self._remote)
        logging.info(FILENAME + ":YOUR IPv6 %s" % self._ipv6)
        return True

    @property
    def local(self):
        if self._local is not None:
            return self._local
        else:
            return None

    @property
    def remote(self):
        if self._remote is not None:
            return self._remote
        else:
            return None

    @property
    def ipv6(self):
        if self._ipv6 is not None:
            return self._ipv6
        else:
            return None

    def ping(self):
        """
        ping
        +OK pong
        """
        logging.info(FILENAME + ": ping")
        self.sock.send("ping")
        ret = self.sock.recv(1024)
        if not ret.startswith("+OK "):
            raise NeedsAuthException(ret)
        else:
            logging.info(FILENAME + ": pong")
        return True

    #override
    def close(self):
        """
        quit
        +OK tunnel server quitting
        """
        #self.quit()
        logging.info(FILENAME + ": quit")
        self.sock.send("quit")
        ret = self.sock.recv(1024)
        if ret.startswith("+OK "):
            return True
        else:
            return False

if __name__ == "__main__":
    HOST="dtcp.feel6.jp"
    PORT="20200"
    #USER=""
    #PASS=""
    TYPE="network"
    DEBUG_LEVEL=10
    dtcpc = DTCPC(HOST,PORT,USER,PASS,TYPE,debug_level=DEBUG_LEVEL)
    import time
    if dtcpc.auth():
        print dtcpc.local
        print dtcpc.remote
        print dtcpc.ipv6
    #print dtcpc.close()
    while True:
        time.sleep(60)
        dtcpc.ping()
