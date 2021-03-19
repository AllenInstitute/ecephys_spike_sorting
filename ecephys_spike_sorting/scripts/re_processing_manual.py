from helpers.re_processing_common import processing_session

session_name = '1044594870_524761_20200820'#test_2019-07-25_18-16-48' #Fill in with appropriate session name
probes_in = [ 'A']#, 'B', 'C', 'D', 'E', 'F']
probe_type = 'PXI'

if __name__ == '__main__':
	processor = processing_session(session_name, probes_in, probe_type)
	processor.start_processing()