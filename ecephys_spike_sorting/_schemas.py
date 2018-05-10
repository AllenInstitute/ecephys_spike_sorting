from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema 
from argschema.fields import Nested 
 
class InputParameters(ArgSchema): 
    # Add your input parameters 
    pass 
 
class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 
    # Add your output parameters 
    pass