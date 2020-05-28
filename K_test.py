import random

def error_n_k(range_n, range_k, iters):
    print("Nodos    K   Erro Relativo (%)")
    for n in range_n:
        print(n)
        for K in range_k:
            error_list = []
            for i in range(iters):
                x = [float("inf")] * K
                for _ in range(n):
                    for i in range(K):
                        v = random.expovariate(1)
                        x[i] = x[i] if x[i] < v else v
                N = (K - 1) / sum(x)
                error = (abs(N - n) / n) * 100
                error_list.append(error)
            print(n, K, sum(error_list) / iters, sep="\t")

error_n_k(list(range(10, 151, 10)), list(map(lambda i: 2 ** i, range(15))), 100)