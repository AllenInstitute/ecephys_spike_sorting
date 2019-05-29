from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ...common.schemas import EphysParams, Directories


class PostprocessingParams(DefaultSchema):
    within_unit_overlap_window = Float(required=False, default=0.000166, help='Time window for removing overlapping spikes for one unit.')
    between_unit_overlap_window = Float(required=False, default=0.000166, help='Time window for removing overlapping spikes between two units.')
    between_unit_channel_distance = Int(required=False, default=5, help='Number of channels (above and below peak channel) to search for overlapping spikes')

class InputParameters(ArgSchema):
    
    ks_postprocessing_params = Nested(PostprocessingParams)
    directories = Nested(Directories)
    ephys_params = Nested(EphysParams)
    

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    execution_time = Float()
    