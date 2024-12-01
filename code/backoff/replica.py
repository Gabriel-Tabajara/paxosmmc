from process import Process
from message import ProposeMessage,DecisionMessage,RequestMessage, ResponseMessage
from utils import *
import time

class Replica(Process):
    def __init__(self, env, id, config):
        Process.__init__(self, env, id)
        self.slot_in = self.slot_out = 1
        self.proposals = {}
        self.decisions = {}
        self.requests = []
        self.config = config
        self.clientsRecord = {}
        self.env.addProc(self)

    def propose(self):
        """
        This function tries to transfer requests from the set requests
        to proposals. It uses slot_in to look for unused slots within
        the window of slots with known configurations. For each such
        slot, it first checks if the configuration for that slot is
        different from the prior slot by checking if the decision in
        (slot_in - WINDOW) is a reconfiguration command. If so, the
        function updates the configuration for slot s. Then the
        function pops a request from requests and adds it as a
        proposal for slot_in to the set proposals. Finally, it sends a
        Propose message to all leaders in the configuration of
        slot_in.
        """
        while len(self.requests) != 0 and self.slot_in < self.slot_out+WINDOW:
            # A reconfiguration command is decided in a slot just like
            # any other command.  However, it does not take effect
            # until WINDOW slots later. This allows up to WINDOW slots
            # to have proposals pending.
            if self.slot_in > WINDOW and self.slot_in-WINDOW in self.decisions:
                if isinstance(self.decisions[self.slot_in-WINDOW].command, ReconfigCommand):
                    r,a,l = self.decisions[self.slot_in-WINDOW].command.config.split(';')
                    self.config = Config(r.split(','), a.split(','), l.split(','))
                    # print self.id, ": new config:", self.config
            if self.slot_in not in self.decisions:
                received_msg = self.requests.pop(0)
                self.proposals[self.slot_in] = received_msg
                for ldr in self.config.leaders:
                    message = ProposeMessage(self.id, self.slot_in, received_msg.command, received_msg.trace_id)
                    # print self.id, ": sending propose", self.slot_in, ":", received_msg.command, "to", ldr
                    self.sendMessage(ldr, message)
            self.slot_in +=1

    def perform(self, msg):
        """
        This function is invoked with the same sequence of commands at
        all replicas. First, it checks to see if it has already
        performed the command. Different replicas may end up proposing
        the same command for different slots, and thus the same
        command may be decided multiple times. The corresponding
        operation is evaluated only if the command is new and it is
        not a reconfiguration request. If so, perform() applies the
        requested operation to the application state. In either case,
        the function increments slot out.
        """
        for s in range(1, self.slot_out):
            if self.decisions[s].command == msg.command:
                self.slot_out += 1
                return
        if isinstance(msg.command, ReconfigCommand):
            self.slot_out += 1
            return
        # print self.id, ": perform", self.slot_out, ":", cmd
        self.slot_out += 1

    def body(self):
        """
        A replica runs in an infinite loop, receiving
        messages. Replicas receive two kinds of messages:

        - Requests: When it receives a request from a client, the
        replica adds the request to set requests. Next, the replica
        invokes the function propose().

        - Decisions: Decisions may arrive out-of-order and multiple
        times. For each decision message, the replica adds the
        decision to the set decisions. Then, in a loop, it considers
        which decisions are ready for execution before trying to
        receive more messages. If there is a decision corresponding to
        the current slot out, the replica first checks to see if it
        has proposed a different command for that slot. If so, the
        replica removes that command from the set proposals and
        returns it to set requests so it can be proposed again at a
        later time. Next, the replica invokes perform().
        """
        print "Here I am: ", self.id
        while not self.stop:
            msg = self.getNextMessage()
            if isinstance(msg, RequestMessage):
                # print self.id, ": received request", msg.command, msg.trace_id
                self.requests.append(msg)
                self.clientsRecord[msg.trace_id] = msg.src
            elif isinstance(msg, DecisionMessage):
                self.decisions[msg.slot_number] = msg
                while self.slot_out in self.decisions:
                    if self.slot_out in self.proposals:
                        if self.proposals[self.slot_out].command != self.decisions[self.slot_out].command:
                            self.requests.append(self.proposals[self.slot_out])
                            # is_ready_for_response = False
                        del self.proposals[self.slot_out]
                    self.perform(self.decisions[self.slot_out])
                # if is_ready_for_response == True:
                if msg.trace_id in self.clientsRecord:
                    client_id = self.clientsRecord[msg.trace_id]
                    slots_to_remove = []
                    for slot in self.proposals:
                        if self.proposals[slot].trace_id == msg.trace_id:
                            slots_to_remove.append(slot)
                    for slot in slots_to_remove:
                        del self.proposals[slot]
                    del self.clientsRecord[msg.trace_id]
                    self.sendMessage(client_id, ResponseMessage(self.id, msg.command, msg.slot_number, trace_id=msg.trace_id))
                    # self.printSlots()
                else:
                    # print "Replica: unknown trace id %s" % (msg)
                    pass
            else:
                # print "Replica: unknown msg type"
                pass
            self.propose()

    def printSlots(self):
        slots_traces = {}
        for self.slot_out in self.decisions:
            slots_traces[self.slot_out] = self.decisions[self.slot_out].trace_id
        print 'Slots: ', slots_traces
        print '\n\n'
     
