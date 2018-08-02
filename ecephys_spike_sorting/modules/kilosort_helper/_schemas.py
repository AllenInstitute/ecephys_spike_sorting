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

    chanMap = String(required=True, default="'chanMap.mat'", help='Path to channel map .mat file')
    trange = String(required=True, default='[0 Inf]', help='Time range in seconds to process')
    fproc = String(required=True, default="fullfile('C:/data/kilosort', 'temp_wh.dat')", help='Processed data file on a fast ssd')
    fbinary = String(required=True, default="fullfile(ops.rootZ, continuous.dat)", help='Path to original data file')
    datatype = String(required=True, default= "'.dat'", help="datatype ('dat', 'bin') or 'openEphys'")
    fshigh = Int(required=True, default=150, help='filter cutoff frequency')
    Th = String(required=True, default='[12 12]', help='threshold (last pass can be lower')
    lam = Int(required=True, default=100)
    mergeThreshold = Float(required=True, default=0.25, help='merge when explained variance loss is below this number as a sqrt fraction of the unit''s mean')
    ccsplit = Float(required=True, default=0.97, help='splitting a cluster at the end requires at least this much isolation (max=1)')
    minFR = Float(required=True, default=1/50., help='minimum spike rate (Hz)')
    ThS = String(required=True, default='[8 8]', help='lower bound on acceptable single spike quality')
    momentum = String(required=True, default='[20 400]', help='number of samples to average over (annealed)')
    sigmaMask = Int(required=True, default=30, help='spatial constant in um for computing ')
    Nfilt = Int(required=True, default=1024, help='max number of clusters (even temporary ones)')
    nPCs = Int(required=True, default=3, help='how many PCs to project the spikes into')
    useRAM = Int(required=True, default=0, help='whether to hold data in RAM (won''t check if there''s enough RAM)')
    ThPre = Int(required=True, default=8, help='threshold crossings for pre-clustering (in PCA projection space)')
    GPU = Int(required=True, default=1, help='whether to run this code on an Nvidia GPU (much faster, mexGPUall first)')
    nSkipCov = Int(required=True, default=5, help='compute whitening matrix from every Nth batch')
    ntbuff = Int(required=True, default=64, help='samples of symmetrical buffer for whitening and spike detection')
    scaleproc = Int(required=True, default=200, help='int16 scaling of whitenend data')
    NT = String(required=True, default='64*1024 + ops.ntbuff', help='this is the batch size; for GPU should be a multiple of 32 + ntbuff)')
    spkTh = Int(required=True, default=-6, help='spike threshold is standard deviations')
    loc_range = String(required=True, default='[5 4]', help='ranges to detect peaks; plus/minus in time and channel')
    long_range = String(required=True, default='[30 6]', help='ranges to detect isolated peaks')
    maskMaxChannels = Int(required=True, default=5, help='how many channels to mask up/down')
    criterionNoiseChannels = Float(required=True, default=0.2, help='fraction of "noise" templates allowed to span all channel groups')
    whiteningRange = Int(required=True, default=32)

class InputParameters(ArgSchema):
    
    kilosort_location = String()
    kilosort_repo = String()
    probe_json = String()
    kilosort_params = Nested(KilosortParameters, required=False)
    kilosort2_params = Nested(Kilosort2Parameters, required=False)
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
    