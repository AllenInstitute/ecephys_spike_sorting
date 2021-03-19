from helpers.full_probe_batch_processing_common import processing_session

session_name = '1044389060_510589_20200819'#test_2019-07-25_18-16-48' #Fill in with appropriate session name
probes_in = [ 'A', 'B', 'C']
probe_type = 'PXI'

if __name__ == '__main__':
	processor = processing_session(session_name, probes_in, probe_type)
	processor.start_processing()