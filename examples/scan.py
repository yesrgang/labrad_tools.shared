# name experiment
# this string will be reformatted by the conductor prepending a (%Y%m%d) 
# datestring and appending an experiment iteratoin number
# e.g. running an experiment with name, 'example-experiment', for the first 
# time on 20181101 will give a reformatted experiment name: 
# 20181101/example-experiment#0
name = 'example-experiment'

# specify looping of parameter values
# set this to true if we would like to infinitely loop parameter values 
# when looping, for each shot, the current value of each parameter is 
# added to the end of the value_queue.
loop = True

# specify which parameters we should reload at the begining of the experiment
# this is useful for reconfiguring the parameter objects for different 
# experiments
reload_parameters = {
    'blue_pmt.recorder': {}
    }

# create lists of parameter values to be scanned through
test_scan_values = range(10)

# assign parameter values
# both values to be scanned through and fixed values are specified here
parameter_values = {
    'test_parameter': test_scan_values,
    'sequencer.sequence': [
        'blue_mot', 
        'red_mot-fast', 
        'load_odt-fast', 
        'load_lattice-fast2', 
        'polarize_p-lat', 
        'rabi_clock-sweep', 
        'pmt-fast-v'
        ],
    }

if __name__ == '__main__':
    from conductor.experiment import Experiment
    my_experiment = Experiment(
        name=name,
        reload_parameters=reload_parameters,
        parameter_values=parameter_values,
        loop=loop,
        )
    my_experiment.queue(run_immedeately=True)
