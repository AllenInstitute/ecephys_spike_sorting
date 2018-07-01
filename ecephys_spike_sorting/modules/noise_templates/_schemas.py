from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, NumpyArray
from ecephys_spike_sorting.common.schemas import EphysParams, Directories

class NoiseWaveformParams(DefaultSchema):
	classifier_path = String(required=True, default='classifier.pkl')
	#std_thresh = Float(required=True, default=2.5)
	#waveform_spread = Int(required=True, default=10)
	#thresh2 = Float(required=True, default=0.2)
	#min_peak_sample = Int(required=True, default=10)
	#min_trough_sample = Int(required=True, default=10)
	#min_height = Int(required=True, default=-5)
	#contamination_ratio = Float(required=True, default=0.01)

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
    