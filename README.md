# NXP Task

### General
On-chip microcontroller peripherals need clock signals for their functionality. The source of these signals
is usually the microcontroller’s bus-clock. Most peripherals need to adjust (decrease) the frequency of
their bus clock to ensure their correct function. This “adjustment” is done through a system of
prescalers (dividers) and multiplexors. A prescaler divides an input frequency by a constant value (in this
task). A multiplexor’s output is one of its input signals.
###
The algorithm is designed to find the best configuration of multiplexors that produces the frequency closest to
the required one. Inputs for the whole algorithm are the following: input clock frequency (BUS_CLOCK)
and required frequency for the peripheral. The results of the algorithm are configurations of
multiplexors and the achieved frequency for the peripheral.

The algorithm is designed in two optimization principles / methods: 

* **Greedy** - algorithm calculates all the possible combinations of multiplexor inputs and for each one calculates
output frequency. The combination of multiplexor inputs with the closest output frequency to the wanted frequency is 
chosen. Problem with this approach is that the complexity rises geometrically with number of multiplexors and might be 
significantly expensive performance-wise.
* **Genetic** - this algorithm uses principles of genetic algorithms. In first round it will generate finite number 
of random combinations of multiplexor inputs, sort them by the vicinity of output frequency to the wanted frequency and 
then will generate new generation of multiplexor input combinations. New generation consists of genetic mutations
  (randomly mixed inputs) of the combinations with best score (output frequency vicinity) and also randomly generated 
combinations. The new generation of multiplexor input combinations are again used in previous procedure. This procedure 
is repeated until the wanted frequency is achieved or iteration limit is triggered. This algorithm is rather stochastic 
and may not lead to deterministic final results. However, might be much more efficient compared to previous greedy algorithm.

### Input YAML clock model config
The whole clock model is represented and defined in input yaml file.
Input yaml has the following structure:
```commandline
model:
  units:

    unit_name ( input | divider | multiplexor| output ) : [list of indexes for each unit type]

  tree:
    unit_name:
        index_of_unit: index_of_port_for_output_of_given_unit 
     (or)
    unit_name: list_of_unit_indexes 

  params:
    unit_name: [list of input parameters for instantiation of units defined in 'units' section]
```
* `units` defines which objects will be instantiated. Input and output objects are necessary.
* `tree` defines the whole structure of dividers and multiplexors. This part represents, where the output from each 
unit is rooted to (see example yaml)
* `params` are input parameters needed at initialization of each object defined in `units` block

Input YAML example is placed in the root of this repo (`model_config_example.yaml`)
### Basic commands
To run our peripheral clock finding script we need to run this command:<br />
`python3 cli.py --model /path/to/clock/model/yaml --wanted-freq [wanted freq as float] ` <br />
we can extend out command with these command-line arguments: 
`--method` for defining method for searching nearest output frequency:<br />
`--method greedy(default) | genetic`<br />
with `genetic` method come these sub command-line arguments: <br />
`--genetic-it` for defining number of iterations of finding optimal multiplexor configuration by genetic algorithm <br />
`--genetic-pop-count` for defining number of iterations of finding optimal multiplexor configuration by genetic algorithm

Try to run:
`python3 cli.py -h` and `python3 cli.py --model model_config_example.yaml` for initial testing
