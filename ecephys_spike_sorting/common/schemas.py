from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, NumpyArray

class EphysParams(DefaultSchema):
	sample_rate = Float(required=True, default=30000.0)
	lfp_sample_rate = Float(require=True, default=2500.0)
	bit_volts = Float(required=True, default=0.195)
	num_channels = Int(required=True, default=384)
	reference_channels = NumpyArray(required=False, default=[37, 76, 113, 152, 189, 228, 265, 304, 341, 380])

class Directories(DefaultSchema):
	kilosort_output_directory = String()
	extracted_data_directory = String()