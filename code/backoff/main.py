# -*- coding: utf-8 -*-

import time
import threading
from env import Env, Config
from client import Client

NREQUESTS = None

def run_experiments(env, initialconfig, max_failures=3, max_clients=200, step=50, duration=60):
    results = {}
    full_config = env.createReplicas(initialconfig)
    full_config = env.createAcceptors(full_config, 0)
    full_config = env.createLeaders(full_config, 0)
    round = 0
    for f in range(1, max_failures + 1): 
        results[f] = []
        print(f'failures: {f}')
        for i in range(f + 1):
            if i > 0:
                env.fail_acceptor(f"acceptor 0.{i - 1}")
        for num_clients in range(step, max_clients + 1, step):
            clients = []
            for i in range(num_clients):
                pid = f"client {round}.{i}"
                client = Client(env, id=pid, config=full_config, duration=duration, max_requests=NREQUESTS)
                clients.append(client)
            round += 1

            for client in clients:
                client.join()

            for client in clients:
                print(f'Client {client.id} finished')
                print(f'Client {client.id} latencies: {client.result}')

            total_throughput = sum(client.result[0] for client in clients if client.result)
            avg_latency = (sum(client.result[1] for client in clients if client.result) / len(clients))
            results[f].append((total_throughput, avg_latency))

            print(f'Results for f = {f} and num_clients = {num_clients}')
            print(f'Total throughput: {total_throughput}')
            print(f'Average latency: {avg_latency}')
    print(f'Results: {results}')
    return results

def write_results(results, max_clients, step):
    for f, data in results.items():
        with open(f"logs/results/2results_f_{f}_mx_{max_clients}_step_{step}.log", "w") as file:
            for throughput, latency in data:
                file.write(f"{throughput} {latency}\n")
    
def main():
    t0 = time.time()
    env = Env()
    max_clients = 250
    step = 50
    initialconfig = Config([], [], [])
    experiment_results = run_experiments(env, initialconfig, max_failures=1, max_clients=max_clients, step=step, duration=90)
    print('Experiment results')
    print(f'Time elapsed: {time.time() - t0}')
    write_results(experiment_results, max_clients, step)

if __name__ == "__main__":
    main()
