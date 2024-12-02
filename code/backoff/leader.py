from utils import *
from process import Process
from commander import Commander
from scout import Scout
from message import ProposeMessage, AdoptedMessage, PreemptedMessage
from time import sleep

class Leader(Process):
    """
    Leader receives requests from replicas, serializes requests and
    responds to replicas. Leader maintains four state variables:
    - ballot_number: a monotonically increasing ballot number
    - active: a boolean flag, initially false
    - proposals: a map of slot numbers to proposed commands in the form
      of a set of (slot number, command) pairs, initially empty.
    - timeout: time in seconds the leader waits between operations
    """
    def __init__(self, env, id, config):
        super().__init__(env, id)
        self.ballot_number = BallotNumber(0, self.id)
        self.active = False
        self.proposals = {}
        self.timeout = 0.0
        self.config = config
        self.env.addProc(self)

    def body(self):
        """
        The leader starts by spawning a scout for its initial ballot
        number, and then enters into a loop awaiting messages.
        """
        print(f"Here I am: {self.id}")
        Scout(
            self.env, 
            f"scout:{self.id}:{self.ballot_number}", 
            self.id, 
            self.config.acceptors, 
            self.ballot_number, 
            None
        )
        while not self.stop:
            msg = self.getNextMessage()
            if isinstance(msg, ProposeMessage):
                # Handle proposal messages
                if msg.slot_number not in self.proposals:
                    self.proposals[msg.slot_number] = msg
                    if self.active:
                        Commander(
                            self.env,
                            f"commander:{self.id}:{self.ballot_number}:{msg.slot_number}",
                            self.id,
                            self.config.acceptors,
                            self.config.replicas,
                            self.ballot_number,
                            msg.slot_number,
                            msg.command,
                            msg.trace_id
                        )
            elif isinstance(msg, AdoptedMessage):
                # Decrease timeout since there's no apparent competition
                if self.timeout > TIMEOUTSUBTRACT:
                    self.timeout -= TIMEOUTSUBTRACT
                if self.ballot_number == msg.ballot_number:
                    pmax = {}
                    # Handle accepted values
                    for pv in msg.accepted:
                        if pv.slot_number not in pmax or pmax[pv.slot_number] < pv.ballot_number:
                            pmax[pv.slot_number] = pv.ballot_number
                            self.proposals[pv.slot_number] = pv
                    # Start commanders for all proposals
                    for sn in self.proposals:
                        Commander(
                            self.env,
                            f"commander:{self.id}:{self.ballot_number}:{sn}",
                            self.id,
                            self.config.acceptors,
                            self.config.replicas,
                            self.ballot_number,
                            sn,
                            self.proposals.get(sn).command,
                            self.proposals.get(sn).trace_id
                        )
                    self.active = True
            elif isinstance(msg, PreemptedMessage):
                if msg.ballot_number.leader_id > self.id:
                    self.timeout *= TIMEOUTMULTIPLY
                if msg.ballot_number > self.ballot_number:
                    self.active = False
                    self.ballot_number = BallotNumber(msg.ballot_number.round + 1, self.id)
                    Scout(
                        self.env, 
                        f"scout:{self.id}:{self.ballot_number}", 
                        self.id, 
                        self.config.acceptors, 
                        self.ballot_number, 
                        msg.trace_id
                    )
            sleep(self.timeout)
