# -*- coding: utf-8 -*-
import threading
from message import RequestMessage
from process import Process
from env import Command
import time

class Client(Process):
    def __init__(self, env, id, config, duration=60, max_requests=None):
        super().__init__(env, id)  # Use Python 3-style super()
        self.duration = duration
        self.max_requests = max_requests
        self.latencies = []
        self.requests_sent = 0
        self.config = config
        self.result = None
        self.env.addProc(self)

    def body(self):
        print(f"Here I am: {self.id}")

        t0 = time.time()

        # Create a thread for sending requests
        doRequest = threading.Thread(target=self.request, args=(t0,))
        doRequest.daemon = True
        doRequest.start()

        # Join thread with timeout equal to duration
        doRequest.join(timeout=self.duration)

        t4 = time.time()
        if t4 - t0 == 0:
            throughput = 0
        else:
            throughput = self.requests_sent / (t4 - t0)

        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0

        # Optionally log the results (uncomment if needed)
        # with open(f"logs/clientes/client_{self.id}_results.log", "w") as log_file:
        #     log_file.write(f"Throughput: {throughput} req/s\n")
        #     log_file.write(f"Average Latency: {avg_latency} s\n")
        #     log_file.write(f"Latencies: {self.latencies}\n")

        self.result = (throughput, avg_latency)

    def request(self, t0):
        while not self.stop:
            t_end = t0 + self.duration
            t1 = time.time()
            if self.max_requests and self.requests_sent >= self.max_requests:
                break
            if t1 >= t_end:
                break

            operation_number = self.id.split('.')[1]
            for r in self.config.replicas:
                cmd = Command(self.id, 0, f"operation 0.{operation_number}")
                self.sendMessage(r, RequestMessage(self.id, cmd))
            msg = self.getNextMessage()  # Assuming this blocks until a message is received

            t2 = time.time()

            self.latencies.append(t2 - t1)
            self.requests_sent += 1
