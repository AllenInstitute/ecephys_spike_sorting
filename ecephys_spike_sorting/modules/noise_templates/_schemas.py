from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, NumpyArray
from ...common.schemas import EphysParams, Directories

class NoiseWaveformParams(DefaultSchema):
    classifier_path = String(required=True, help='Path to pre-trained waveform classifier')

    smoothed_template_amplitude_threshold = Float(default=0.2, help='Fraction of max amplitude for calculating spread')
    template_amplitude_threshold = Float(default=0.2, help='Fraction of max amplitude for calculating spread')
    smoothed_template_filter_width = Int(default=2, help='Smoothing window for calculating spread')
    min_spread_threshold = Int(default=2, help='Minimum number of channels for a waveform to be considered good')
    mid_spread_threshold = Int(default=16, help='Over this channel spread, waveform shape must be considered')
    max_spread_threshold = Int(default=25, help='Maximum channel spread for a good unit')

    channel_amplitude_thresh = Float(default=0.25, help='Fraction of max amplitude for considering channels in spatial peak detection')
    peak_height_thresh = Float(default=0.2, help='Minimum height for spatial peak detection')
    peak_prominence_thresh = Float(default=0.2, help='Minimum prominence for spatial peak detection')
    peak_channel_range = Int(default=24, help='Range of channels for detecting spatial peaks')
    peak_locs_std_thresh = Float(default=3.5, help='Maximum standard deviation of peak locations for good units')

    min_temporal_peak_location = Int(default=10, help='Minimum peak index for good unit')
    max_temporal_peak_location = Int(default=30, help='Maximum peak index for good unit')

    template_shape_channel_range = Int(default=12, help='Range of channels for checking template shape')
    wavelet_index = Int(default=2, help='Wavelet index for noise template shape detection')
    min_wavelet_peak_height = Float(default=0.0, help='Minimum wavelet peak height for good units')
    min_wavelet_peak_loc = Int(default=15, help='Minimum wavelet peak location for good units')
    max_wavelet_peak_loc = Int(default=25, help='Maximum wavelet peak location for good units')

    multiprocessing_worker_count = Int(default=4, help='Number of workers to use for spatial peak calculation')

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
    