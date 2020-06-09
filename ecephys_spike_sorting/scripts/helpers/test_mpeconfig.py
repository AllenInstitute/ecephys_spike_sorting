import mpe_config

config = mpe_config.source_configuration('neuropixels')

computer = config['openEphys']['host']
print(computer)