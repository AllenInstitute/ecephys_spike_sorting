from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ecephys_spike_sorting.common.schemas import EphysParams, Directories

class MeanWaveformParams(DefaultSchema):
	samples_per_spike = Int(required=True, default=82)
	pre_samples = Int(required=True, default=20)
	num_epochs = Int(required=True, default=10)
	spikes_per_epoch = Int(require=True, default=100)

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
    mean_waveforms_file = String()
    