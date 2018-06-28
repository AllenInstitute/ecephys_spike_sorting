from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, NumpyArray

class NoiseWaveformParams(DefaultSchema):


class EphysParams(DefaultSchema):
	sample_rate = Float(required=True, default=30000.0)
    bit_volts = Float(required=True, default=0.195)
    num_channels = Int(required=True, default=384)
    reference_channels = NumpyArray(required=False, default=[37, 76, 113, 152, 189, 228, 265, 304, 341, 380])

class Directories(DefaultSchema):
	kilosort_output_directory = InputDir()
	extracted_data_directory = InputDir()

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
    