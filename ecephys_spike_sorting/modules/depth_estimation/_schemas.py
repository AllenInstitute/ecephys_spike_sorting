from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, Bool
 

class InputParameters(ArgSchema): 
    extracted_data_directory = String()
    save_depth_estimation_figure = Bool()
    depth_estimation_figure_location = String()

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 
    surface_channel = Int()
    air_channel = Int()
    probe_json = String()
    