from helpers.batch_processing_common import processing_session

session = '1030680600_498756_20200618'
probes_in = ['A', 'B', 'C',]
probe_type = 'PXI'

if __name__ == '__main__':
	processor = processing_session(session_name, probes_in, probe_type)
	processor.start_processing()