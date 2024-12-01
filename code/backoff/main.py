# -*- coding: utf-8 -*-

import time
import threading
from env import Env, Config
from client import Client

NACCEPTORS = 7
NREPLICAS = 3
NLEADERS = 3
NREQUESTS = 1

def run_experiments(env, initialconfig, max_failures=3, max_clients=200, step=50, duration=60):
    results = {}
    full_config = env.createReplicas(initialconfig)
    full_config = env.createAcceptors(full_config, 0)
    full_config = env.createLeaders(full_config, 0)
    round = 0
    for f in range(0, max_failures + 1): 
        results[f] = []
        print 'failures: {}'.format(f)
        for i in range(f + 1):
            if i > 0:
                env.fail_acceptor("acceptor 0.%d" % (i - 1))
        for num_clients in range(step, max_clients + 1, step):
            clients = []
            for i in range(num_clients):
                pid = "client %d.%d" % (round,i)
                client = Client(env, id=pid, config=full_config, duration=duration, max_requests=NREQUESTS)
                clients.append(client)
            round += 1

            for client in clients:
                client.join()

            for client in clients:
                print 'Client {} finished'.format(client.id)
                print 'Client {} latencies: {}'.format(client.id, client.result)

            total_throughput = sum(client.result[0] for client in clients if client.result)
            avg_latency = (sum(client.result[1] for client in clients if client.result) / len(clients))
            results[f].append((total_throughput, avg_latency))

            print 'Results for f = {} and num_clients = {}'.format(f, num_clients)
            print 'Total throughput: {}'.format(total_throughput)
            print 'Average latency: {}'.format(avg_latency)
    print 'Results: {}'.format(results)
    return results

def write_results(results, max_clients, step):
    for f, data in results.items():
        with open("logs/testes/results_f_{}_mx_{}_step_{}.log".format(f, max_clients, step), "w") as f:
            for throughput, latency in data:
                f.write("{} {}\n".format(throughput, latency))
    
def main():
    t0 = time.time()
    env = Env()
    max_clients = 60
    step = 20
    initialconfig = Config([], [], [])
    experiment_results = run_experiments(env, initialconfig, max_failures=1, max_clients=max_clients, step=step, duration=25)
    print 'Experiment results'
    print 'Time elapsed: {}'.format(time.time() - t0)
    write_results(experiment_results, max_clients, step)

if __name__ == "__main__":
    main()
