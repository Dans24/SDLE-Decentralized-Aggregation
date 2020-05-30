import ExtremaAllNeighbours as ExtAllNeigh
import ExtremaAllNeighboursSingle as ExtAllNeighSingle
import ExtremaTimeoutNoWait as ExtAllNeighNoWait
import ExtremaTimeoutNoWaitChange as ExtAllNeighNoWaitChange
import Simulator_Statistics as Analyzer

analyser = Analyzer.Simulator_Analyzer()
range_n = [3, 7]  # range(10, 201, 20)
range_K = [3, 7]  # [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
n_iters = 3  # 10
kwargs = []

def analize_n():
    print("Analysing variable N")
    kwargs = []
    for n in range_n:
        args = (n, 128, 5)
        kwarg = {"max_dist": 20, "drop_chance": 0.0}
        kwargs.append((args, kwarg))

    # No TArgs
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeigh.simulatorGeneratorArgs, kwargs, 100,
                                  title="Extrema Propagation All Neighbors K=100 T=25  Drop=0%", results_name="Erro relativo (%)")
    # No TArgs
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighSingle.simulatorGeneratorArgs, kwargs, 100,
                                  title="Extrema Propagation All Neighbors Single K=100 T=25 Drop=20%", results_name="Erro relativo (%)")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWait.simulatorGeneratorTArgs, kwargs, 100,
                                  title="Extrema Propagation No Wait K=100 Drop=0%", results_name="Erro relativo (%)")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWaitChange.simulatorGeneratorTArgs, kwargs, 100,
                                  title="Extrema Propagation No Wait with Change K=100 T=25% Drop=0%", results_name="Erro relativo (%)")

def analyse_K():
    print("Analysing variable K")
    kwargs = []
    for k in range_K:
        args = (5, k, 25)
        kwarg = {"max_dist": 20, "drop_chance": 0.0}
        kwargs.append((args, kwarg))

    #No TArgs
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeigh.simulatorGeneratorArgs, kwargs, 100,
                                 title="Extrema Propagation All Neighbors n=100 T=25 Drop=0%", results_name="Erro relativo (%)")
    #No TArgs
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighSingle.simulatorGeneratorArgs, kwargs, 100,
                                  title="Extrema Propagation All Neighbors Single n=100 T=25 Drop=0%", results_name="Erro relativo (%)")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWait.simulatorGeneratorTArgs, kwargs, 100,
                                  title="Extrema Propagation No Wait n=100 Drop=0%", results_name="Erro relativo (%)")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWaitChange.simulatorGeneratorTArgs, kwargs, 100,
                                 title="Extrema Propagation No Wait with Change n=100 Drop=0%", results_name="Erro relativo (%)")

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
        args = (n, 128, 25)
        kwarg = {"max_dist": 20,  "drop_chance": 0.0}
        kwargs.append((args, kwarg))

    # analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeigh.simulatorGeneratorTArgs, kwargs, 100,
    # title="Extrema Propagation All Neightbours n=100 Drop=0%", results_name="Erro relativo (%)")
    # analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighSingle.simulatorGeneratorArgsT, kwargs, 100,
    # title="Extrema Propagation n=100 T=25% Drop=0%", results_name="Erro relativo (%)")
    #analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWait.simulatorGeneratorTArgs, kwargs, 100,
    #                              title="Extrema Propagation n=100 Drop=0%", results_name="Erro relativo (%)")
    #analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWaitChange.simulatorGeneratorTArgs, kwargs,
    #                              100, title="Extrema Propagation K=100 T=25% Drop=0%",
    #                              results_name="Erro relativo (%)")


analize_n()
analyse_K()
