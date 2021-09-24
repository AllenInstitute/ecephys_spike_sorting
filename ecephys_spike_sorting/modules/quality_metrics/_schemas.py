from argschema import ArgSchema, ArgSchemaParser 
from argschema.schemas import DefaultSchema
from argschema.fields import Nested, InputDir, String, Float, Dict, Int, Boolean
from ...common.schemas import EphysParams, Directories, WaveformMetricsFile, ClusterMetricsFile


class QualityMetricsParams(DefaultSchema):
    isi_threshold = Float(required=False, default=0.0015, help='Maximum time (in seconds) for ISI violation')
    min_isi = Float(required=False, default=0.00, help='Minimum time (in seconds) for ISI violation')
    tbin_sec = Float(required=False, default=0.001, help='time bin in seconds for ccg in contam_rate calculation')
    max_radius_um = Int(required=False, default=68, help='Maximum radius for computing PC metrics, in um')
    max_spikes_for_unit = Int(required=False, default=500, help='Number of spikes to subsample for computing PC metrics')
    max_spikes_for_nn = Int(required=False, default=10000, help='Further subsampling for NearestNeighbor calculation')
    n_neighbors = Int(required=False, default=4, help='Number of neighbors to use for NearestNeighbor calculation')
    n_silhouette = Int(required=False, default=10000, help='Number of spikes to use for calculating silhouette score')

    drift_metrics_min_spikes_per_interval = Int(required=False, default=10, help='Minimum number of spikes for computing depth')
    drift_metrics_interval_s = Float(required=False, default=100, help='Interval length is seconds for computing spike depth')
    include_pcs = Boolean(required=False, default=True, help='Set to false if features were not saved with Phy output')

class InputParameters(ArgSchema):
    
    quality_metrics_params = Nested(QualityMetricsParams)
    ephys_params = Nested(EphysParams)
    directories = Nested(Directories)
    waveform_metrics = Nested(WaveformMetricsFile)
    cluster_metrics = Nested(ClusterMetricsFile)
    
class OutputSchema(DefaultSchema): 
    input_parameters = Nested(InputParameters, 
                              description=("Input parameters the module " 
                                           "was run with"), 
                              required=True) 
 
class OutputParameters(OutputSchema): 

    execution_time = Float()
    quality_metrics_output_file = String()
    