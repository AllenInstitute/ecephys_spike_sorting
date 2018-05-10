import subprocess
from . import entrypoint_exists

DEFAULT_ENTRYPOINT = 'ecephys_spike_sorting'

from ecephys_spike_sorting import __version__

def test_default_entrypoint_installed():
    assert entrypoint_exists(DEFAULT_ENTRYPOINT)

def test_version():
    p = subprocess.Popen('%s --version' % DEFAULT_ENTRYPOINT, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()

    assert output.strip().decode('UTF-8') == __version__ or err.strip().decode('UTF-8') == __version__

def test_input_json_schema():
    
    p = subprocess.Popen('%s --input_json example.json' % DEFAULT_ENTRYPOINT, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    output, err = p.communicate()
    assert str('marshmallow.exceptions.ValidationError') in str(err)
