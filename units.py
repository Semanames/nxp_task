import abc


class Unit:
    '''
    Basic building blocks (Unit objects) for creating the ClockModel object
    Each Unit has a set of inputs (collection of other Unit objects) and method get_output_signal,
    which processes raw signal (frequency) from active input unit.
    '''
    @abc.abstractmethod
    def get_active_input_unit(self):
        ...

    def get_output_signal(cls, signal: float) -> float:
        return signal


class Input(Unit):

    def __init__(self, input_data: float):
        self.input_data = input_data

    @property
    def inputs(self):
        return self.input_data

    def get_active_input_unit(self):
        return self.input_data


class Output(Unit):
    def __init__(self):
        self._inputs = []

    @property
    def inputs(self):
        return self._inputs

    def get_active_input_unit(self):
        return self.inputs[0]


class Divider(Unit):

    def __init__(self, divisor: float):
        self.divisor = divisor
        self._inputs = []

    @property
    def inputs(self):
        return self._inputs

    def get_active_input_unit(self):
        return self.inputs[0]

    def get_output_signal(self, signal):
        return signal/self.divisor


class Multiplexor(Unit):
    def __init__(self, active_slot):
        self._inputs = {}  # dictionary for mapping particular input slot to input Unit object
        self.active_input_slot = active_slot

    @property
    def inputs(self):
        return self._inputs

    @property
    def enumerated_ports(self):
        return dict(enumerate(self._inputs.keys()))

    def get_active_input_unit(self):
        return self._inputs[self.active_input_slot]

