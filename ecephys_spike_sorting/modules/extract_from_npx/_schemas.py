from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ...common.schemas import EphysParams, Directories, CommonFiles

class ExtractFromNpxParams(DefaultSchema):
    npx_directory = String(help='Path to NPX file(s) saved by Open Ephys')
    settings_xml = String(help='Path to settings.xml file saved by Open Ephys')
    npx_extractor_executable = String(help='Path to .exe file for NPX extraction (Windows only)')
    npx_extractor_repo = String(required=False, default='None', help='Path to local repository for NPX extractor')

class InputParameters(ArgSchema): 
    extract_from_npx_params = Nested(ExtractFromNpxParams)
    directories = Nested(Directories)
    common_files = Nested(CommonFiles)

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 
    npx_extractor_execution_time = Float()
    settings_json = String()
    npx_extractor_commit_hash = String()
    npx_extractor_commit_date = String()
    