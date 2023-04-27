import argparse
import yaml
from model import ClockModel
from peripheral_clock_calculation import GeneticMultiplexorAdjuster, GreedyMultiplexorAdjuster


class PeripheralClockCalculationHandler:

    def __init__(self, cli_args: argparse.Namespace):
        self.clock_model = self.create_clock_model_from_input_yaml(cli_args.model)
        self.wanted_frequency = cli_args.wanted_freq
        self.genetic_population_count = cli_args.genetic_pop_count
        self.genetic_number_of_iterations = cli_args.genetic_it
        self.multiplexor_adjuster = GeneticMultiplexorAdjuster(
            clock_model=self.clock_model,
            population_count=self.genetic_population_count,
            num_iterations=self.genetic_number_of_iterations
        ) if cli_args.method == 'genetic' else GreedyMultiplexorAdjuster(clock_model=self.clock_model)

    @staticmethod
    def create_clock_model_from_input_yaml(path_to_model_yaml) -> ClockModel:

        with open(path_to_model_yaml) as stream:
            config = yaml.safe_load(stream)

        clock_model = ClockModel()
        clock_model.load_model_from_config(config)
        return clock_model

    def run_calculation(self):
        output_freq, mpx_config = self.multiplexor_adjuster.calculate_nearest_output_frequency(self.wanted_frequency)

        for i, port in enumerate(mpx_config):
            print(f'Multiplexor {i+1} active input : {port}')

        print(f'Achieved frequency: {output_freq} MHz')
