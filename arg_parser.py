import argparse


class ClockModelArgumentParser(argparse.ArgumentParser):
    '''
    Parser of input argument vector for clock model calculation
    '''

    def __init__(self,
                 description='CLI interface to calculate nearest output frequency for peripheral '
                             'devices processed by a model predefined system of prescalers and multiplexors',
                 *args,
                 **kwargs):
        super().__init__(description, *args, **kwargs)

        self.add_argument('--model', help='path to clock model yaml')
        self.add_argument('--wanted-freq', type=float, help='wanted frequency on the output for the model')
        self.add_argument('--method', choices=['greedy', 'genetic'], default='greedy',
                          help='method for calculating nearest output peripheral frequency:'
                               ' "greedy" or "genetic" could be used')
        self.add_argument('--genetic-it', help='number of iterations for genetic algorithm')
        self.add_argument('--genetic-pop-count', help='number of possible combinations for multiplexor ports')

    def parse_args(self, *args, **kwargs) -> argparse.Namespace:
        arguments = super().parse_args(*args, **kwargs)

        if arguments.method != 'genetic' and arguments.genetic_it:
            self.error('--genetic-it can only be set when --method=genetic.')

        if arguments.method != 'genetic' and arguments.genetic_pop_count:
            self.error('--genetic-pop-count can only be set when --method=genetic.')

        if arguments.method == 'genetic' and arguments.genetic_pop_count is None:
            print('Setting population count to 100')
            arguments.genetic_pop_count = 100

        if arguments.method == 'genetic' and arguments.genetic_it is None:
            print('Setting number of iterations to 1000')
            arguments.genetic_it = 1000

        return arguments
