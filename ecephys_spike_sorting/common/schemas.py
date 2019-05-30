from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, NumpyArray

class EphysParams(DefaultSchema):
    sample_rate = Float(required=True, default=30000.0, help='Sample rate of Neuropixels AP band continuous data')
    lfp_sample_rate = Float(require=True, default=2500.0, help='Sample rate of Neuropixels LFP band continuous data')
    bit_volts = Float(required=True, default=0.195, help='Scalar required to convert int16 values into microvolts')
    num_channels = Int(required=True, default=384, help='Total number of channels in binary data files')
    reference_channels = NumpyArray(required=False, default=[36, 75, 112, 151, 188, 227, 264, 303, 340, 379], help='Reference channels on Neuropixels probe (numbering starts at 0)')
    template_zero_padding = Int(required=True, default=21, help='Zero-padding on templates output by Kilosort')
    vertical_site_spacing = Float(required=False, default=20e-6) 

class Directories(DefaultSchema):
    kilosort_output_directory = String()
    extracted_data_directory = String()