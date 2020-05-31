import ExtremaAllNeighbours as ExtAllNeigh
import ExtremaTimeoutNoWait as ExtAllNeighNoWait
import ExtremaTimeoutNoWaitChange as ExtAllNeighNoWaitChange
import Simulator_Statistics as Analyzer

analyser = Analyzer.Simulator_Analyzer()
range_n = range(10, 201, 20)
range_K = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
n_iters = 25
kwargs = []

def analize_n(Ts):
    print("Analysing variable N")
    kwargs = []
    for T in Ts:
        argss = []
        for n in range_n:
            args = (n, 128, T)
            kwarg = {
                "max_dist": 20,
                "drop_chance": 0.0,
                "timeout": float("inf"),
                "network_change_time": float("inf")
            }
            argss.append((args, kwarg))
        kwargs.append(argss)

    # No TArgs
    print("All Neighbours N, no network change")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeigh.simulatorGeneratorArgs, kwargs[0], n_iters,
                                  title="Extrema Propagation All Neighbors K=128 T=2  Drop=0%", results_name="Erro relativo (%)")
    # No TArgs
    print("No Wait N, no network change")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWait.simulatorGeneratorArgs, kwargs[1], n_iters,
                                  title="Extrema Propagation No Wait K=128 T=10 Drop=0%", results_name="Erro relativo (%)")
    print("No Wait Change N, no network change")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWaitChange.simulatorGeneratorArgs, kwargs[2], n_iters,
                                  title="Extrema Propagation No Wait with Change K=128 T=5 Drop=0%", results_name="Erro relativo (%)")

def analyse_K():
    print("Analysing variable K")
    kwargs = []
    for k in range_K:
        args = (10, k, 25)
        kwarg = {
            "max_dist": 20,
            "drop_chance": 25.0,
            "timeout": float("inf"),
            "network_change_time": float("inf")
        }
        kwargs.append((args, kwarg))

    #No TArgs
    analyser.analyze_gen_variable("Variação de K", range_K, ExtAllNeigh.simulatorGeneratorArgs, kwargs, n_iters,
                                 title="Extrema Propagation All Neighbors n=10 Drop=25%", results_name="Erro relativo (%)")
    analyser.analyze_gen_variable("Variação de K", range_K, ExtAllNeighNoWait.simulatorGeneratorTArgs, kwargs, n_iters,
                                  title="Extrema Propagation No Wait n=10 Drop=25%", results_name="Erro relativo (%)")
    analyser.analyze_gen_variable("Variação de K", range_K, ExtAllNeighNoWaitChange.simulatorGeneratorTArgs, kwargs, n_iters,
                                 title="Extrema Propagation No Wait with Change n=10 Drop=25%", results_name="Erro relativo (%)")

def analyze_T():
    print("Analysing variable T")
    kwargsExtAllNeigh = []
    kwargsAllNeighSingle = []
    kwargsExtllNeighNoWait= []
    kwargsExtAllNeighNoWaitChange = []
    #After getting perfect T em ralação a N
    range_T_ExtAllNeigh = {}
    range_T_ExtAllNeighSingle = {}
    range_T_ExtAllNeighNoWait = {}
    range_T_ExtAllNeighNoWaitChange = {}

    for n in range_n:
        args = (n, 128)
        kwarg = {
            "max_dist": 20,
            "drop_chance": 0.0,
            "timeout": float("inf"),
            "network_change_time": float("inf")
        }
        kwargs.append((args, kwarg))

    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeigh.simulatorGeneratorTArgs, kwargs, n_iters,
        title="Extrema Propagation All Neightbours K=128 Drop=0%", results_name="T")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWait.simulatorGeneratorTArgs, kwargs, n_iters,
        title="Extrema Propagation No Wait K=128 Drop=0%", results_name="T")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWaitChange.simulatorGeneratorTArgs, kwargs, n_iters,
        title="Extrema Propagation No Wait Change K=128 Drop=0%", results_name="T")

#analyze_T()
#analize_n([1, 5, 10])
analyse_K()
