from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ecephys_spike_sorting.common.schemas import EphysParams, Directories


class QualityMetricsParams(DefaultSchema):
    isi_threshold = Float(required=True, default=0.015, help='Maximum time (in seconds) for ISI violation')
    snr_spike_count = Int(required=True, default=100, help='Number of waveforms used to compute SNR')
    samples_per_spike = Int(required=True, default=82, help='Number of samples to extract for each spike')
    pre_samples = Int(required=True, default=20, help='Number of samples between start of spike and the peak')
    mean_waveform_diff_thresh = Float(required=True, help='Parameter for determining noisy channels to ignore')

class InputParameters(ArgSchema):
    
    quality_metrics_params = Nested(QualityMetricsParams)
    ephys_params = Nested(EphysParams)
    directories = Nested(Directories)
    
    mean_waveforms_file = String(required=True, help='Path to mean waveforms file (.npy)')

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    execution_time = Float()
    quality_metrics_output_file = String()
    