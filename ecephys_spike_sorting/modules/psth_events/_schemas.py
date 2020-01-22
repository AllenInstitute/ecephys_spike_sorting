from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ...common.schemas import EphysParams, Directories


class psth_params(DefaultSchema):
    event_ex_param_str = String(required=True, default='XD=4,1,50', help="parameter string in CatGT used for extraction, e.g. 'XD=4,1,50' or 'SY=0,384,6,500'")


class InputParameters(ArgSchema):
    psth_events = Nested(psth_params)
    directories = Nested(Directories)
    ephys_params = Nested(EphysParams)

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    execution_time = Float()
    