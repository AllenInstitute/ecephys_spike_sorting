from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ...common.schemas import EphysParams, Directories, CommonFiles

class MedianSubtractionParams(ArgSchema):
    median_subtraction_executable = String(help='Path to .exe used for median subtraction (Windows only)')
    median_subtraction_repo = String(help='Path to local repository for median subtraction executable')

class InputParameters(ArgSchema): 

    median_subtraction_params = Nested(MedianSubtractionParams)
    common_files = Nested(CommonFiles)
    directories = Nested(Directories)
    ephys_params = Nested(EphysParams)
    
class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 
    median_subtraction_execution_time = Float()
    median_subtraction_commit_hash = String()
    median_subtraction_commit_date = String()
    