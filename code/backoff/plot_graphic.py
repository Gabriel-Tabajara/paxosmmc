import matplotlib.pyplot as plt

def plot_results(results):
    plt.figure(figsize=(10, 6))

    for f, data in results.items():
        throughputs, latencies = zip(*data)
        plt.plot(throughputs, latencies, label="f = {}".format(f))

    plt.title("Curvas de Vazão x Latência")
    plt.xlabel("Vazão (Requisições por Segundo)")
    plt.ylabel("Latência Média (s)")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    results = {}
    with open("logs/testes/results_f_1_mx_30_step_10.log", "r") as f:
        results[1] = [tuple(map(float, line.split())) for line in f.readlines()]
    plot_results(results)