from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
 

class InputParameters(ArgSchema):
    
    kilosort_location = String()
    input_file_location = String()
    num_channels = Int()
    

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 
    # Add your output parameters 
    execution_time = Float()
    