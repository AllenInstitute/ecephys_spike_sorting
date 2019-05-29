from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ...common.schemas import EphysParams, Directories

class MeanWaveformParams(DefaultSchema):
    samples_per_spike = Int(required=True, default=82, help='Number of samples to extract for each spike')
    pre_samples = Int(required=True, default=20, help='Number of samples between start of spike and the peak')
    num_epochs = Int(required=True, default=1, help='Number of epochs to compute mean waveforms')
    spikes_per_epoch = Int(require=True, default=100, help='Max number of spikes per epoch')
    upsampling_factor = Float(require=False, default=2.439, help='Upsampling factor for calculating waveform metrics')

class InputParameters(ArgSchema):
    
    mean_waveforms_file = String(required=True, help='Path to mean waveforms file (.npy)')
    waveforms_metrics_file = String(required=True, help='Path to mean waveforms metrics file (.csv)')
    nwb_file = String(required=False, help='Path to NWB file for extracting epochs')

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
    