from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ...common.schemas import EphysParams, Directories


class AutomergingParams(DefaultSchema):
    merge_threshold = Float(required=True, default=2.5, help='Minimum merge score required to perform a merge')
    distance_to_compare = Int(required=True, default=5, help='Distance (in channels) to look for potential merges')

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
    