from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
 

class InputParameters(ArgSchema): 
    oe_json_file = String()
    probe_info_file = String()
    output_file_location = String()
    executable_file = String()
    surface_channel = Int()
    air_channel = Int()
    

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 
    # Add your output parameters 
    execution_time = Float()
    