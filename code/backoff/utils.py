from collections import namedtuple

WINDOW = 5               # Number of slots that can have proposals pending
TIMEOUTMULTIPLY = 1.2    # Multiplicative increase amount for liveness timeouts
TIMEOUTSUBTRACT = 0.03   # Additive decrease amount for liveness timeouts

class BallotNumber(namedtuple('BallotNumber', ['round', 'leader_id'])):
    """
    A ballot number is a lexicographically ordered pair of an integer
    and the identifier of the ballot's leader.
    """
    __slots__ = ()
    
    def __str__(self):
        return "BN({}, {})".format(self.round, self.leader_id)

class PValue(namedtuple('PValue', ['ballot_number', 'slot_number', 'command', 'trace_id'])):
    """
    PValue is a triple consisting of a ballot number, a slot number, and a command.
    """
    __slots__ = ()
    
    def __str__(self):
        return "PV({}, {}, {}, {})".format(self.ballot_number, self.slot_number, self.command, self.trace_id)

class Command(namedtuple('Command', ['client', 'req_id', 'op'])):
    """
    A command consists of the process identifier of the client
    submitting the request, a client-local request identifier, and an
    operation (which can be anything).
    """
    __slots__ = ()
    
    def __str__(self):
        return "Command({}, {}, {})".format(self.client, self.req_id, self.op)

class ReconfigCommand(namedtuple('ReconfigCommand', ['client', 'req_id', 'config'])):
    """
    A reconfiguration command is a command sent by a client to
    reconfigure the system.  A reconfiguration command consists of the
    process identifier of the client submitting the request, a
    client-local request identifier, and a configuration.
    """
    __slots__ = ()
    
    def __str__(self):
        return "ReconfigCommand({}, {}, {})".format(self.client, self.req_id, self.config)

class Config(namedtuple('Config', ['replicas', 'acceptors', 'leaders'])):
    """
    A configuration consists of a list of replicas, a list of
    acceptors, and a list of leaders.
    """
    __slots__ = ()
    
    def __str__(self):
        return "{};{};{}".format(','.join(self.replicas), ','.join(self.acceptors), ','.join(self.leaders))
