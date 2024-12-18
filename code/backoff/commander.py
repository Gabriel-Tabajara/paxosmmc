from message import P2aMessage, P2bMessage, PreemptedMessage, DecisionMessage
from process import Process
from utils import Command

class Commander(Process):
    """
    The commander runs what is known as phase 2 of the Synod
    protocol. Every commander is created for a specific ballot
    number, slot number, and command triple.
    """
    def __init__(self, env, id, leader, acceptors, replicas,
                 ballot_number, slot_number, command, trace_id):
        super().__init__(env, id)  # Use Python 3-style super()
        self.leader = leader
        self.acceptors = acceptors
        self.replicas = replicas
        self.ballot_number = ballot_number
        self.slot_number = slot_number
        self.command = command
        self.trace_id = trace_id
        self.env.addProc(self)

    def body(self):
        """
        A commander sends a p2a message to all acceptors and waits
        for p2b responses. In each such response, the ballot number in the
        message will be compared to the commander's ballot number.
        There are two cases:

        - If a commander receives p2b messages with its ballot number
        from all acceptors in a majority of acceptors, then the
        commander learns that the command has been chosen for the
        slot. In this case, the commander notifies all replicas and
        exits.

        - If a commander receives a p2b message with a different
        ballot number from some acceptor, then it learns that a higher
        ballot is active. This means that the commander's
        ballot number may no longer be able to make progress. In this
        case, the commander notifies its leader about the existence of
        the higher ballot number and exits.
        """
        waitfor = set()
        for acceptor in self.acceptors:
            self.sendMessage(
                acceptor,
                P2aMessage(self.id, self.ballot_number, self.slot_number, self.command, self.trace_id)
            )
            waitfor.add(acceptor)

        while not self.stop:
            msg = self.getNextMessage()
            if isinstance(msg, P2bMessage):
                if self.ballot_number == msg.ballot_number and msg.src in waitfor:
                    waitfor.remove(msg.src)
                    if len(waitfor) < len(self.acceptors) / 2:
                        for replica in self.replicas:
                            self.sendMessage(
                                replica,
                                DecisionMessage(self.id, self.slot_number, self.command, msg.trace_id)
                            )
                        return
                else:
                    self.sendMessage(
                        self.leader,
                        PreemptedMessage(self.id, msg.ballot_number, msg.trace_id)
                    )
                    return
        self.stop_process()
