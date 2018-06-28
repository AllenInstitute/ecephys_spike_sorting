from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ecephys_spike_sorting.common.schemas import EphysParams, Directories


class AutomergingParams(DefaultSchema):
    merge_threshold = Float(required=True, default=2.5)

class InputParameters(ArgSchema):
    
    automerging_params = Nested(AutomergingParams)
    ephys_params = Nested(EphysParams)
    directories = Nested(Directories)

class OutputSchema(DefaultSchema): 

    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    execution_time = Float()
    