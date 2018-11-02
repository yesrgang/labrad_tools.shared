import json
import labrad

def json_defaults(obj):
    if type(obj).__name__ == 'ndarray':
        return obj.tolist()

class Experiment(object):
    def __init__(self, **kw):
        self.name = kw.get('name', 'default')
        self.reload_parameters = kw.get('reload_parameters', {})
        self.parameter_values = kw.get('parameter_values', {})
        self.loop = kw.get('loop', False)

    def queue(self, run_immedeately=False):
        cxn = labrad.connect()
        request = {
            'name': self.name,
            'reload_parameters': self.reload_parameters,
            'parameter_values': self.parameter_values,
            'loop': self.loop,
            }
        request_json = json.dumps(request, default=json_defaults)
        if run_immedeately:
            cxn.conductor.queue_experiment(request_json, True)
            cxn.conductor.stop_experiment()
        else:
            cxn.conductor.queue_experiment(request_json)


