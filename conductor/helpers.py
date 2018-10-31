def sort_by_priority(parameters):
    return sorted([parameter_name for parameter_name in parameters], 
                  key=lambda x: parameters[x].priority)

def get_remaining_points(parameters):
    return max([len(parameter.value_queue) for parameter in parameters.values()])

