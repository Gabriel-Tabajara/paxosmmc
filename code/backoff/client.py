# -*- coding: utf-8 -*-
from message import RequestMessage
from process import Process
from env import Command
import time

class Client(Process):
    def __init__(self, env, id, config, duration=60, max_requests=None):
        super(Client, self).__init__(env, id)
        self.duration = duration
        self.max_requests = max_requests
        self.latencies = []
        self.requests_sent = 0
        self.config = config
        self.result = None
        self.env.addProc(self)

    def body(self):
        print 'Here I am: ', self.id

        t0 = time.time()
        while True:
            t_end = t0 + self.duration
            t1 = time.time()
            # print 'Time: {} ClientId: {}\n'.format(t1 - (t0 + self.duration), self.id)
            if self.max_requests and self.requests_sent >= self.max_requests:
                break
            if t1 >= t_end:
                # print 'Time: {} ClientId: {}'.format(t1 - (t0 + self.duration), self.id)
                break

            # Monta requisição
            # cmd = Command(self.id, 0, "operation {}.{}".format(self.id, self.requests_sent))
            # request_message = RequestMessage(self.id, cmd)
            operation_number = self.id.split('.')[1]
            for r in self.config.replicas:
                cmd = Command(self.id,0,"operation %d.%s" % (0,operation_number))
                self.sendMessage(r, RequestMessage(self.id,cmd))
            msg = self.getNextMessage()
            # if msg.trace_id == self.id:
            #     print 'Received message: {} {}'.format(self.id, msg)
            # else: 
            #     print 'Received message with wrong trace_id: {} {}'.format(self.id, msg)

            t2 = time.time()

            # Loga latência
            self.latencies.append(t2 - t1)
            self.requests_sent += 1
            # print 'Client {} sent request {}'.format(self.id, self.requests_sent)

        t4 = time.time()
        if t4 - t0 == 0:
            throughput = 0
        else:
            throughput = self.requests_sent / (t4 - t0)

        # Calcula métricas
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0

        # Loga os resultados
        # log_file = open("logs/clientes/client_{}_results.log".format(self.id), "w")
        # log_file.write("Throughput: {} req/s\n".format(throughput))
        # log_file.write("Average Latency: {} s\n".format(avg_latency))
        # log_file.write("Latencies: {}\n".format(self.latencies))
        # log_file.close()
        # print 'Client {} finished'.format(self.id)
        self.result = (throughput, avg_latency)