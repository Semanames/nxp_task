from typing import Union

from units import Input, Divider, Multiplexor, Output, Unit


class ClockModel:
    """
    Represents a state of given clock model with defined active inputs.
    Class can be extended by several building methods based on particular interest.
    Method load_model_from_config builds clock model defined by yaml
    (or other data-holding format) config represented by dict structure.
    """

    def __init__(self):
        self.input_unit = []
        self.multiplexors = []
        self.dividers = []
        self.output_unit = []

    def get_output_signal(self) -> float:
        return self.get_signal_from(self.output_unit[0])

    def load_model_from_config(self, config: dict):
        '''
        Method builds model from input dict:
        { model:
            {units : ... Unit objects which are going to be instantiated
             tree : ... Input relations between particular Unit Objects
             params: ... Input params needed for above defined Unit objects
            }
        }
        :param config: dict
        :return: None
        '''

        unit_name_mapping = {'input': self.input_unit,
                             'divider': self.dividers,
                             'multiplexor': self.multiplexors,
                             'output': self.output_unit}

        for unit_name, num in config['model']['units'].items():

            if unit_name == 'input':
                for i, index in enumerate(num):
                    self.input_unit.append(Input(config['model']['params']['input'][i]))

            elif unit_name == 'divider':
                for divisor in config['model']['params']['divider']:
                    self.dividers.append(Divider(divisor))

            elif unit_name == 'multiplexor':
                for i, index in enumerate(num):
                    self.multiplexors.append(Multiplexor(config['model']['params']['multiplexor'][i]))

            elif unit_name == 'output':
                for _ in num:
                    self.output_unit.append(Output())

            else:
                raise ClockModelError(f'No such input unit name {unit_name}')

        for unit_name, connections in config['model']['tree'].items():
            for unit_index, sub_units in connections.items():
                for sub_unit_name, indexes in sub_units.items():
                    if sub_unit_name == 'multiplexor':
                        for index, input_num in indexes.items():
                            try:
                                unit_name_mapping[sub_unit_name][index].inputs[input_num] = unit_name_mapping[unit_name][unit_index]
                            except Exception as e:
                                ClockModelError(str(e))
                    else:
                        for index in indexes:
                            try:
                                unit_name_mapping[sub_unit_name][index].inputs.append(unit_name_mapping[unit_name][unit_index])
                            except Exception as e:
                                ClockModelError(str(e))

    @staticmethod
    def get_signal_from(unit: Union[float, Unit]) -> float:
        '''
        Recursive function that goes bottom-up from selected
        Unit we would like to get the output from, to the Input Unit
        :param unit: Unit
        :return: float
        '''
        if isinstance(unit, float):
            return unit
        input_unit = unit.get_active_input_unit()
        signal_from_input_unit = ClockModel.get_signal_from(input_unit)
        output_signal = unit.get_output_signal(signal_from_input_unit)
        return output_signal

class ClockModelError(Exception): pass
