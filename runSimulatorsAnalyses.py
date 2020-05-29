import ExtremaAllNeighbours as ExtAllNeigh
import ExtremaAllNeighboursSingle as ExtAllNeighSingle
import ExtremaTimeoutNoWait as ExtAllNeighNoWait
import ExtremaTimeoutNoWaitChange as ExtAllNeighNoWaitChange
import Simulator_Statistics as Analyzer

analyser = Analyzer.Simulator_Analyzer()
range_n = [5, 10]  # range(10, 201, 20)
range_K = [5, 10]  # [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
n_iters = 3  # 10
kwargs = []

def analize_n():
    kwargs = []
    for n in range_n:
        args = (n, 128, 25)
        kwarg = {"max_dist": 20}
        kwargs.append((args, kwarg))

    #analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeigh.simulatorGeneratorTArgs, kwargs, 100,
    # title="Extrema Propagation All Neightbours K=100 Drop=0%", results_name="Erro relativo (%)")
    #analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighSingle.simulatorGeneratorArgsT, kwargs, 100,
    # title="Extrema Propagation K=100 T=25% Drop=20%", results_name="Erro relativo (%)")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWait.simulatorGeneratorTArgs, kwargs, 100,
                                  title="Extrema Propagation K=100 Drop=0%", results_name="Erro relativo (%)")
    #analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWaitChange.simulatorGeneratorTArgs, kwargs, 100,
    #                              title="Extrema Propagation K=100 T=25% Drop=0%", results_name="Erro relativo (%)")

def analyse_K():
    kwargs = []
    for k in range_K:
        args = (100, k, 25)
        kwarg = {"max_dist": 20}
        kwargs.append((args, kwarg))

    #analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeigh.simulatorGeneratorTArgs, kwargs, 100,
    # title="Extrema Propagation All Neightbours n=100 Drop=0%", results_name="Erro relativo (%)")
    #analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighSingle.simulatorGeneratorArgsT, kwargs, 100,
    # title="Extrema Propagation n=100 T=25% Drop=0%", results_name="Erro relativo (%)")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWait.simulatorGeneratorTArgs, kwargs, 100,
                                  title="Extrema Propagation n=100 Drop=0%", results_name="Erro relativo (%)")
    #analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWaitChange.simulatorGeneratorTArgs, kwargs, 100,
    #                             title="Extrema Propagation K=100 T=25% Drop=0%", results_name="Erro relativo (%)")

def analyze_T():
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
        kwarg = {"max_dist": 20}
        kwargs.append((args, kwarg))

    # analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeigh.simulatorGeneratorTArgs, kwargs, 100,
    # title="Extrema Propagation All Neightbours n=100 Drop=0%", results_name="Erro relativo (%)")
    # analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighSingle.simulatorGeneratorArgsT, kwargs, 100,
    # title="Extrema Propagation n=100 T=25% Drop=0%", results_name="Erro relativo (%)")
    analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWait.simulatorGeneratorTArgs, kwargs, 100,
                                  title="Extrema Propagation n=100 Drop=0%", results_name="Erro relativo (%)")
    #analyser.analyze_gen_variable("Número de nodos", range_n, ExtAllNeighNoWaitChange.simulatorGeneratorTArgs, kwargs,
    #                              100, title="Extrema Propagation K=100 T=25% Drop=0%",
    #                              results_name="Erro relativo (%)")


analize_n()
analyse_K()