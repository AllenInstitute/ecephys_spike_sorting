from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, List, Boolean
from ...common.schemas import EphysParams, Directories
from ..catGT_helper._schemas import CatGTParams


class tPrimeParams(DefaultSchema):
    tPrime_path = InputDir(help='directory containing the TPrime executable.')
    sync_period = Float(default=1.0, help='Period of sync waveform (sec).')
    toStream_sync_params = String(required=False, default='SY=0,384,6,500', help='string of CatGT params used to extract to stream sync edges, e.g. SY=0,384,6,500')
    ni_sync_params = String(required=False, default='XA=0,1,3,500', help='string of CatGT params used to extract NI sync edges, e.g. XA=0,1,3,500')
    ni_ex_list = String(required=False, default='', help='string of CatGT params used to extract edges from ni, e.g. XA=0,1,3,500')
    im_ex_list = String(required=False, default='', help='string of CatGT params used to extract edges from im streams, e.g. SY=0,384,6,500')
    tPrime_3A = Boolean(required=False, default=False, help='is this 3A data?')
    toStream_path_3A = String(required=False, help='full path to toStream edges file')
    fromStream_list_3A = List(String, required=False, help='list of full paths to fromStream edges files')

class InputParameters(ArgSchema):
    tPrime_helper_params = Nested(tPrimeParams)
    catGT_helper_params = Nested(CatGTParams)
    directories = Nested(Directories)
    ephys_params = Nested(EphysParams)

class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    execution_time = Float()
    