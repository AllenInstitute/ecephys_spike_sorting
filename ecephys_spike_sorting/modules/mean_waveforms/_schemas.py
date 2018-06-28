from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ecephys_spike_sorting.common.schemas import EphysParams, Directories

class MeanWaveformParams(DefaultSchema):
	n_boots = Int(required=True, default=100)
	samples_per_spike = Int(required=True, default=82)
	pre_samples = Int(required=True, default=20)
	total_waveforms = Int(required=True, default=100)

class InputParameters(ArgSchema):
    
    mean_waveform_params = Nested(MeanWaveformParams)
    ephys_params = Nested(EphysParams)
    directories = Nested(Directories)

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    execution_time = Float()
    