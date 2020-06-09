from helpers.batch_processing_common import processing_session

session = '856549794_443087_20190424'
probes_in = ['D', 'E', 'F']#'A', 'B', 'C',
probe_type = 'PXI'

if __name__ == '__main__':
	processor = processing_session(session_name, probes_in, probe_type)
	processor.start_processing()