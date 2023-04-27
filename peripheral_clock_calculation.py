import abc
import math
import random
from functools import partial
from typing import Tuple, List, Set, Any

from model import ClockModel


class BaseMultiplexorAdjuster:
    '''
    Base class for MultiplexorAdjusters.
    Implementations of this class should represent different approaches for finding the closest output frequency
    to wanted frequency
    '''

    def __init__(self, clock_model: ClockModel):
        self.clock_model = clock_model

    @abc.abstractmethod
    def calculate_nearest_output_frequency(self, wanted_frequency: float) -> Tuple[float, List[int]]:
        pass

    def set_multiplexor_configuration(self, mpx_configuration: list):
        for multiplexor, selected_slot in zip(self.clock_model.multiplexors, mpx_configuration):
            multiplexor.active_input_slot = selected_slot

    def evaluate_multiplexor_configuration(self, mpx_configuration: list, wanted_frequency: float) -> Tuple[float, float]:
        self.set_multiplexor_configuration(mpx_configuration)
        output_signal = self.clock_model.get_output_signal()
        calc_freq_difference = abs(output_signal - wanted_frequency)
        return calc_freq_difference, output_signal


class GreedyMultiplexorAdjuster(BaseMultiplexorAdjuster):

    '''
    Implementation of greedy algorithm for finding wanted frequency.
    Algorithm calculates all the possible combinations of multiplexor inputs
    and for each one calculates output frequency. The combination of multiplexor inputs
    with the closest output frequency to the wanted frequency is chosen.
    '''

    def calculate_nearest_output_frequency(self, wanted_frequency: float) -> Tuple[float, List[int]]:

        multiplexor_inputs_count = [len(mpx.inputs) for mpx in self.clock_model.multiplexors]
        multiplexor_port_mapping = [mpx.enumerated_ports for mpx in self.clock_model.multiplexors]

        # Generating all possible input port combinations
        mpx_configurations = list(
            map(lambda comb: [multiplexor_port_mapping[i][j] for i, j in enumerate(comb)],
                self.calculate_combinations(multiplexor_inputs_count)
                )
        )  # This construction simply maps general number combinations to port combinations

        frequency_difference = math.inf
        selected_mpx_configuration = []
        selected_output_signal = 0.0

        for mpx_configuration in mpx_configurations:

            calc_freq_difference, output_signal = self.evaluate_multiplexor_configuration(
                mpx_configuration,
                wanted_frequency
            )

            if calc_freq_difference < frequency_difference:
                frequency_difference = calc_freq_difference
                selected_mpx_configuration = mpx_configuration
                selected_output_signal = output_signal

        self.set_multiplexor_configuration(selected_mpx_configuration)

        return selected_output_signal, selected_mpx_configuration

    def calculate_combinations(self, input_list: list) -> List[List[int]]:
        if input_list:
            combination_list = []
            for i in range(input_list[0]):
                combinations = self.calculate_combinations(input_list[1:])
                if combinations:
                    for combination in combinations:
                        ll = [i]
                        ll.extend(combination)
                        combination_list.append(ll)
                else:
                    combination_list.append([i])

            return combination_list
        else:
            return []


class GeneticMultiplexorAdjuster(BaseMultiplexorAdjuster):

    '''
    Implementation of genetic algorithm for finding wanted frequency.
    In first round it will generate finite number of random combinations
    of multiplexor inputs, sort them by the vicinity of output frequency
    to the wanted frequency and then will generate new generation of multiplexor
    input combinations. New generation consists of genetic mutations (randomly mixed inputs)
    of the combinations with best score (output frequency vicinity) and also randomly
    generated combinations. The new generation of multiplexor input combinations are
    again used in previous procedure within the while loop.
    '''

    def __init__(self, clock_model: ClockModel, population_count: int, num_iterations: int):
        super().__init__(clock_model)
        self.population_count = population_count
        self.num_iterations = num_iterations

    def calculate_nearest_output_frequency(self, wanted_frequency):
        multiplexor_inputs_count = [len(mpx.inputs) for mpx in self.clock_model.multiplexors]
        multiplexor_port_mapping = [mpx.enumerated_ports for mpx in self.clock_model.multiplexors]

        # This construction simply maps general number combinations to port combinations
        population_of_mpx_config = list(map(lambda comb: [multiplexor_port_mapping[i][j] for i, j in enumerate(comb)],
                                        self.generate_random_combinations(
                                            self.population_count,
                                            multiplexor_inputs_count)
                                            )
                                        )

        sorting_function = partial(self.evaluate_multiplexor_configuration, wanted_frequency=wanted_frequency)

        it = 0
        while it <= self.num_iterations:
            population_of_mpx_config.sort(key=lambda x: sorting_function(x)[0])
            best_child, second_best_child = population_of_mpx_config[0], population_of_mpx_config[1]
            best_calc_freq_difference, best_output_signal = self.evaluate_multiplexor_configuration(
                best_child,
                wanted_frequency
            )

            if best_output_signal == wanted_frequency:
                return best_output_signal, best_child

            del population_of_mpx_config[2:]

            best_children = self.generate_population_from_parents(
                best_child,
                second_best_child,
                self.population_count//2
            )
            new_children = list(map(lambda x: [multiplexor_port_mapping[i][j] for i, j in enumerate(x)],
                                    self.generate_random_combinations(
                                        self.population_count//2,
                                        multiplexor_inputs_count)
                                    )
                                )

            population_of_mpx_config.extend(best_children)
            population_of_mpx_config.extend(new_children)
            it += 1

        population_of_mpx_config.sort(key=lambda x: sorting_function(x)[0])
        best_calc_freq_difference, best_output_signal = self.evaluate_multiplexor_configuration(
            population_of_mpx_config[0],
            wanted_frequency
        )
        return best_output_signal, population_of_mpx_config[0]

    @staticmethod
    def generate_population_from_parents(parent1: List[int],
                                         parent2: List[int],
                                         population_count: int,
                                         dominance_ratio: float = 0.5) -> List[Tuple[Any]]:
        '''
        Method for generation of  mutations of parent combinations
        :param parent1: Input combination with best results
        :param parent2: Input combination with second best results
        :param population_count: number of children generated from parents
        :param dominance_ratio: dominance of parent1 (best one) over parent2,
                                value from 0 (zero dominance) to 1 (maximal dominance)
        :return: list of new combined combinations
        '''
        new_population = []
        for _ in range(population_count):
            new_child = []
            for slot1, slot2 in zip(parent1, parent2):
                if random.uniform(0.0, 1.0) < dominance_ratio:
                    new_child.append(slot1)
                else:
                    new_child.append(slot2)
            new_population.append(tuple(new_child))
        return list(set(new_population))

    @staticmethod
    def generate_random_combinations(number_of_combinations: int, input_list: List[int]) -> List[Tuple[int]]:
        random_combinations = []
        for _ in range(number_of_combinations):
            random_combinations.append(tuple([random.randint(0, i-1) for i in input_list]))
        return list(set(random_combinations))
