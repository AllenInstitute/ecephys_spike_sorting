from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int
from ecephys_spike_sorting.common.schemas import EphysParams, Directories

class KilosortParameters(DefaultSchema):

	Nfilt = Int(required=True, default=1024)
	Threshold = String(required=True, default="[4, 10, 10]")
	lam = String(required=True, default="[5, 20, 20]")
	IntitalizeTh = Int(required=True, default=-4)
	InitializeNfilt = Int(required=True, default=10000)
    
class Kilosort2Parameters(DefaultSchema):

	Nfilt = Int(required=True, default=1024)
	Threshold = String(required=True, default="[4, 10, 10]")
	lam = String(required=True, default="[5, 20, 20]")
	InitializeTh = Int(required=True, default=-4)
	InitializeNfilt = Int(required=True, default=10000)

class InputParameters(ArgSchema):
    
    kilosort_location = String()
    kilosort_repo = String()
    probe_json = String()
    kilosort_params = Nested(KilosortParameters, required=False)
    kilosort2_params = Nested(KilosortParameters, required=False)
    directories = Nested(Directories)
    ephys_params = Nested(EphysParams)
    kilosort_version = Int(required=True, default=2)
    surface_channel_buffer = Int(required=True, default=15)
    

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    execution_time = Float()
    kilosort_commit_hash = String()
    kilosort_commit_date = String()
    