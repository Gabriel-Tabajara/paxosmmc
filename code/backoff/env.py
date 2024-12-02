import os
import signal
import sys
import time
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from process import Process
from replica import Replica
from utils import *

NACCEPTORS = 7
NREPLICAS = 1
NLEADERS = 1

# Nao usado na implementacao do T2
NREQUESTS = 1
# Nao usado na implementacao do T2
NCONFIGS = 3

class Env:
    """
    This is the main code in which all processes are created and run. This
    code also simulates a set of clients submitting requests.
    """
    def __init__(self):
        self.procs = {}

    def sendMessage(self, dst, msg):
        if dst in self.procs:
            self.procs[dst].deliver(msg)

    def addProc(self, proc):
        self.procs[proc.id] = proc
        proc.start()

    def removeProc(self, pid):
        del self.procs[pid]

    def createReplicas(self, initialconfig):
        for i in range(NREPLICAS):
            pid = f"replica {i}"
            Replica(self, pid, initialconfig)
            initialconfig.replicas.append(pid)
        return initialconfig
    
    def createAcceptors(self, initialconfig, c):
        for i in range(NACCEPTORS):
            pid = f"acceptor {c}.{i}"
            Acceptor(self, pid)
            initialconfig.acceptors.append(pid)
        return initialconfig
    
    def createLeaders(self, initialconfig, c):
        for i in range(NLEADERS):
            pid = f"leader {c}.{i}"
            Leader(self, pid, initialconfig)
            initialconfig.leaders.append(pid)
        return initialconfig
    
    def fail_acceptor(self, id):
        if id in self.procs:
            self.procs[id].stop_process()

    def run(self):
        initialconfig = Config([], [], [])
        c = 0

        # Create replicas
        for i in range(NREPLICAS):
            pid = f"replica {i}"
            Replica(self, pid, initialconfig)
            initialconfig.replicas.append(pid)
        # Create acceptors (initial configuration)
        for i in range(NACCEPTORS):
            pid = f"acceptor {c}.{i}"
            Acceptor(self, pid)
            initialconfig.acceptors.append(pid)
        # Create leaders (initial configuration)
        for i in range(NLEADERS):
            pid = f"leader {c}.{i}"
            Leader(self, pid, initialconfig)
            initialconfig.leaders.append(pid)
        # Send client requests to replicas
        for i in range(NREQUESTS):
            pid = f"client {c}.{i}"
            for r in initialconfig.replicas:
                cmd = Command(pid, 0, f"operation {c}.{i}")
                self.sendMessage(r, RequestMessage(pid, cmd))
                time.sleep(1)

        # Create new configurations
        for c in range(1, NCONFIGS):
            config = Config(initialconfig.replicas, [], [])
            # Create acceptors in the new configuration
            for i in range(NACCEPTORS):
                pid = f"acceptor {c}.{i}"
                Acceptor(self, pid)
                config.acceptors.append(pid)
            # Create leaders in the new configuration
            for i in range(NLEADERS):
                pid = f"leader {c}.{i}"
                Leader(self, pid, config)
                config.leaders.append(pid)
            # Send reconfiguration request
            for r in config.replicas:
                pid = f"master {c}.{i}"
                cmd = ReconfigCommand(pid, 0, str(config))
                self.sendMessage(r, RequestMessage(pid, cmd))
                time.sleep(1)
            # Send WINDOW noops to speed up reconfiguration
            for i in range(WINDOW - 1):
                pid = f"master {c}.{i}"
                for r in config.replicas:
                    cmd = Command(pid, 0, "operation noop")
                    self.sendMessage(r, RequestMessage(pid, cmd))
                    time.sleep(1)
            # Send client requests to replicas
            for i in range(NREQUESTS):
                pid = f"client {c}.{i}"
                for r in config.replicas:
                    cmd = Command(pid, 0, f"operation {c}.{i}")
                    self.sendMessage(r, RequestMessage(pid, cmd))
                    time.sleep(1)

    def terminate_handler(self, signum, frame):
        self._graceexit()

    def _graceexit(self, exitcode=0):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(exitcode)

def main():
    e = Env()
    signal.signal(signal.SIGINT, e.terminate_handler)
    signal.signal(signal.SIGTERM, e.terminate_handler)
    e.run()

if __name__ == '__main__':
    main()
