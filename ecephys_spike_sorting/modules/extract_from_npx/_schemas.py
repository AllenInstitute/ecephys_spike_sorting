from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ecephys_spike_sorting.common.schemas import EphysParams, Directories

class InputParameters(ArgSchema): 
    npx_file = String()
    settings_xml = String()
    npx_extractor_executable = String()
    npx_extractor_repo = String()
    directories = Nested(Directories)

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 
    # Add your output parameters 
    npx_extractor_execution_time = Float()
    settings_json = String()
    npx_extractor_commit_hash = String()
    npx_extractor_commit_date = String()
    