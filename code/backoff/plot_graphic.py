import matplotlib.pyplot as plt

def plot_results(results,f):
    plt.figure(figsize=(10, 6))

    throughputs, latencies = zip(*results)
    plt.plot(throughputs, latencies, label="f = {}".format(f), marker='o')

    plt.title("Curvas de Vazão x Latência")
    plt.xlabel("Vazão (Requisições por Segundo)")
    plt.ylabel("Latência Média (s)")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    results = {}
    f = 0
    with open(f"logs/results/results_f_{f}_mx_250_step_50.log", "r") as file:
        results = [tuple(map(float, line.split())) for line in file.readlines()]
    plot_results(results, f)