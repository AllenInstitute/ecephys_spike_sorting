from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, Bool
 

class InputParameters(ArgSchema): 
    oe_json_file = String()
    input_file = String()
    save_figure = Bool()
    figure_location = String()
    

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 
    # Add your output parameters 
    surface_channel = Int()
    air_channel = Int()
    output_json = String()
    