import statistics
import string
import logging
import logging.config
import pylab

import discrete_event_simulator

class Run_Statistics:
    def __init__(self, tempo_min, tempo_med, tempo_max, n_mensagens_min, n_mensagens_med, n_mensagens_max , results_min, results_med, results_max):
        self.tempo_min = tempo_min
        self.tempo_med = tempo_med
        self.tempo_max = tempo_max
        self.n_mensagens_min = n_mensagens_min
        self.n_mensagens_med = n_mensagens_med
        self.n_mensagens_max = n_mensagens_max
        self.results_min = results_min
        self.results_med = results_med
        self.results_max = results_max


class Simulator_Statistics:

    def __init__(self):
        self.tempo_mins = []
        self.tempo_meds = []
        self.tempo_maxs = []
        self.n_mensagens_mins = []
        self.n_mensagens_meds = []
        self.n_mensagens_maxs = []
        self.results_mins = []
        self.results_meds = []
        self.results_maxs = []

    def add_statistic(self, statistic: Run_Statistics):
        self.tempo_mins.append(statistic.tempo_min)
        self.tempo_meds.append(statistic.tempo_med)
        self.tempo_maxs.append(statistic.tempo_max)
        self.n_mensagens_mins.append(statistic.n_mensagens_min)
        self.n_mensagens_meds.append(statistic.n_mensagens_med)
        self.n_mensagens_maxs.append(statistic.n_mensagens_max)
        self.results_mins.append(statistic.results_min)
        self.results_meds.append(statistic.results_med)
        self.results_maxs.append(statistic.results_max)

    def clear(self):
        self.tempo_mins = []
        self.tempo_meds = []
        self.tempo_maxs = []
        self.n_mensagens_mins = []
        self.n_mensagens_meds = []
        self.n_mensagens_maxs = []
        self.results_mins = []
        self.results_meds = []
        self.results_maxs = []


    def multiple_runs_with_generator(self, n_iter, gen, args):
        times = []
        n_messages = []
        results = []
        for i in range(n_iter):
            # logger_file = simulator.get_logger_file()
            # if logger_file is not None:
            #    logger_id = logger_file
            #    setup_logger(logger_id, logger_file)
            simulator = gen(args[0], args[1])
            simulator.start()
            num_events = len(simulator.get_message_events())
            last_event = simulator.get_events()[num_events - 1]
            (last_time, _) = last_event
            n_messages.append(num_events)
            times.append(last_time)
            results.append(simulator.result())
            print(round((i / n_iter) * 100, 1), "%")
        tempo_min = min(times)
        tempo_med = statistics.mean(times)
        tempo_max = max(times)
        n_mensagens_min = min(n_messages)
        n_mensagens_med = statistics.mean(n_messages)
        n_mensagens_max = max(n_messages)
        results_min = min(map(lambda r: r[0], results)) if len(results) > 0 else None
        results_med = statistics.mean(map(lambda r: r[1], results)) if len(results) > 0 else None
        results_max = max(map(lambda r: r[2], results)) if len(results) > 0 else None
        # if logger_file is not None:
        #    self.print_logs(logger_file, times, n_messages)
        return Run_Statistics(tempo_min, tempo_med, tempo_max, n_mensagens_min, n_mensagens_med, n_mensagens_max,
                              results_min, results_med, results_max)

    def multiple_runs(self, simulator: [discrete_event_simulator]):
        n_iter = len(simulator)
        times = []
        n_messages = []
        results = []
        for i in range(n_iter):
            #logger_file = simulator.get_logger_file()
            #if logger_file is not None:
            #    logger_id = logger_file
            #    setup_logger(logger_id, logger_file)
            simulator[i].start()
            num_events = len(simulator[i].get_message_events())
            last_event = simulator[i].get_events()[num_events - 1]
            (last_time, _) = last_event
            n_messages.append(num_events)
            times.append(last_time)
            results.append(simulator[i].result())
            print(round((i / n_iter) * 100, 1), "%")
        tempo_min = min(times)
        tempo_med = statistics.mean(times)
        tempo_max = max(times)
        n_mensagens_min = min(n_messages)
        n_mensagens_med = statistics.mean(n_messages)
        n_mensagens_max = max(n_messages)
        results_min = min(map(lambda r: r[0], results)) if len(results) > 0 else None
        results_med = statistics.mean(map(lambda r: r[1], results)) if len(results) > 0 else None
        results_max = max(map(lambda r: r[2], results)) if len(results) > 0 else None
        #if logger_file is not None:
        #    self.print_logs(logger_file, times, n_messages)
        return Run_Statistics(tempo_min, tempo_med, tempo_max, n_mensagens_min, n_mensagens_med, n_mensagens_max, results_min, results_med, results_max)

    def print_logs(self, logger_id: string, times, n_messages):
        tempo_min = min(times)
        tempo_med = statistics.mean(times)
        tempo_max = max(times)
        n_mensagens_min = min(n_messages)
        n_mensagens_med = statistics.mean(n_messages)
        n_mensagens_max = max(n_messages)
        print_log("Tempo mínimo: " + str(tempo_min), logger_id)
        print_log("Tempo médio: " + str(tempo_med), logger_id)
        print_log("Tempo máximo: " + str(tempo_max), logger_id)
        print_log("Numero mensagens minimo: " + str(n_mensagens_min), logger_id)
        print_log("Numero mensagens médio: " + str(n_mensagens_med), logger_id)
        print_log("Numero mensagens máximo: " + str(n_mensagens_max), logger_id)


class Simulator_Analyzer:
    def __init__(self):
        self.simulator_statistics = Simulator_Statistics()

    def analyze_variable(self, var_name: string, variable_values, simulators: [[discrete_event_simulator]],
                         n_runs: int, title="", results_name=""):
        num_simulations = 0
        for simulator in simulators:
            statistics_from_runs = self.simulator_statistics.multiple_runs(simulator)
            self.simulator_statistics.add_statistic(statistics_from_runs)
            num_simulations += 1
            print("\rCompletado ", num_simulations , "/" , len(simulators))
        create_plots(self.simulator_statistics, variable_values, var_name, title, results_name=results_name)
        self.simulator_statistics.clear()

    def analyze_gen_variable(self, var_name : string, variable_values, simulatorGen, argss : ([],[]),
                             n_runs: int, title="", results_name=""):
        for args in argss:
            print(str(args))
            statistics_from_runs = self.simulator_statistics.multiple_runs_with_generator(n_runs, simulatorGen, args)
            self.simulator_statistics.add_statistic(statistics_from_runs)
        create_plots(self.simulator_statistics, variable_values, var_name, title, results_name=results_name)
        self.simulator_statistics.clear()

def setup_logger(logger_name, log_file, level=logging.INFO):
    log_setup = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    log_setup.setLevel(level)
    log_setup.addHandler(fileHandler)
    log_setup.addHandler(streamHandler)

def print_log(msg, loggerId):
    logger = logging.getLogger(loggerId)
    logger.info(msg)

def draw_in_plot(ys, xs):
    if len(ys) > 1 and len(xs) > 1:
        pylab.plot(xs, ys)
    else:
        print("Couldn't display plot " + str(xs) + "; " + str(ys))


def save_plot(name, x_label, y_label, title):
    pylab.xlabel(str(x_label))
    pylab.ylabel(str(y_label))
    pylab.title(str(title))
    pylab.savefig('./plots/' + name)
    pylab.clf()


def create_plots(stats: Simulator_Statistics, variable, variable_name: string, title, results_name: string = "", tempo = True, mensagens = True):
    if tempo:
        draw_in_plot(stats.tempo_mins, variable)
        draw_in_plot(stats.tempo_meds, variable)
        draw_in_plot(stats.tempo_maxs, variable)
        save_plot(title + "_" + variable_name + "_times", variable_name, "Time", title)
    if mensagens:
        draw_in_plot(stats.n_mensagens_mins, variable)
        draw_in_plot(stats.n_mensagens_meds, variable)
        draw_in_plot(stats.n_mensagens_maxs, variable)
        save_plot(title + "_" + variable_name + "_n_messages", variable_name, "Number Of messages", title)
    if stats.results_mins != None:
        draw_in_plot(stats.results_mins, variable)
        draw_in_plot(stats.results_meds, variable)
        draw_in_plot(stats.results_maxs, variable)
        save_plot(title + "_" + variable_name + "_" + results_name, variable_name, results_name, title)