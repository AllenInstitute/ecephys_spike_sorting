from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
 

class InputParameters(ArgSchema):
    
    raw_data_location = String()
    spike_times_location = String()
    spike_clusters_location = String()
    num_channels = Int()
    

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 
    # Add your output parameters 
    execution_time = Float()
    