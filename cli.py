from arg_parser import ClockModelArgumentParser
from handler import PeripheralClockCalculationHandler

clock_model_input_parser = ClockModelArgumentParser()
parsed_cli_arguments = clock_model_input_parser.parse_args()
calc_handler = PeripheralClockCalculationHandler(parsed_cli_arguments)

if __name__ == '__main__':
    calc_handler.run_calculation()
