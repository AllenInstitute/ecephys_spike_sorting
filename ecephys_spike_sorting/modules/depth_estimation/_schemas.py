from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, NumpyArray, String, Float, Dict, Int, Bool, OutputFile
from ecephys_spike_sorting.common.schemas import EphysParams, Directories

class DepthEstimationParams(DefaultSchema):
    hi_noise_thresh = Float(required=True, default=50.0)
    lo_noise_thresh = Float(required=True, default=3.0)

    save_figure = Bool(required=True, default=True)
    figure_location = OutputFile(required=True, default=None)
    
    smoothing_amount = Int(required=True, default=5)
    power_thresh = Float(required=True, default=2.5)
    diff_thresh = Float(required=True, default=-0.07)
    freq_range = NumpyArray(required=True, default=[0,10])
    max_freq = Int(required=True, default=150)
    channel_range = NumpyArray(required=True, default=[370,380])
    n_passes = Int(required=True, default=1)
    nfft = Int(required=True, default=4096)

    air_gap = Int(required=True, default=100)
    skip_s_per_pass = Int(required=True, default=100)

class InputParameters(ArgSchema):
    
    depth_estimation_params = Nested(DepthEstimationParams)
    ephys_params = Nested(EphysParams)
    directories = Nested(Directories)

class OutputSchema(DefaultSchema): 

    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    surface_channel = Int()
    air_channel = Int()
    probe_json = String()
    execution_time = Float()  