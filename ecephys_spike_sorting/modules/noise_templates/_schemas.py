from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, NumpyArray
from ...common.schemas import EphysParams, Directories

class NoiseWaveformParams(DefaultSchema):
	classifier_path = String(required=True, default='classifier.pkl', help='Path to waveform classifier')

class InputParameters(ArgSchema):
    
    noise_waveform_params = Nested(NoiseWaveformParams)
    ephys_params = Nested(EphysParams)
    directories = Nested(Directories)
    
class OutputSchema(DefaultSchema): 

    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    execution_time = Float()
    