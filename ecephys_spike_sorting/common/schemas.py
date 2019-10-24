from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, OutputDir, String, Float, Dict, Int, NumpyArray, Bool

class EphysParams(DefaultSchema):
    sample_rate = Float(required=True, default=30000.0, help='Sample rate of Neuropixels AP band continuous data')
    lfp_sample_rate = Float(require=True, default=2500.0, help='Sample rate of Neuropixels LFP band continuous data')
    bit_volts = Float(required=True, default=0.195, help='Scalar required to convert int16 values into microvolts')
    num_channels = Int(required=True, default=384, help='Total number of channels in binary data files')
    reference_channels = NumpyArray(required=False, default=[36, 75, 112, 151, 188, 227, 264, 303, 340, 379], help='Reference channels on Neuropixels probe (numbering starts at 0)')
    template_zero_padding = Int(required=True, default=21, help='Zero-padding on templates output by Kilosort')
    vertical_site_spacing = Float(required=False, default=20e-6, help='Vertical site spacing in meters') 
    probe_type = String(required=False, default='3A', help='3A, 3B1, or 3B2')
    lfp_band_file = String(required=False, help='Location of LFP band binary file')
    ap_band_file = String(required=False, help='Location of AP band binary file')
    reorder_lfp_channels = Bool(required=False, default=True, help='Should we fix the ordering of LFP channels (necessary for 3a probes following extract_from_npx modules)')
    cluster_group_file_name = String(required=False, default='cluster_group.tsv')

class Directories(DefaultSchema):

    kilosort_output_directory = OutputDir(help='Location of Kilosort output files')
    extracted_data_directory = OutputDir(help='Location for NPX file extraction')

class CommonFiles(DefaultSchema):

    probe_json = String(help='Location of probe JSON file')
    settings_json = String(help='Location of settings JSON written by extract_from_npx module')

class WaveformMetricsFile(DefaultSchema):
    waveform_metrics_file = String(help='Location of waveform metrics CSV')
