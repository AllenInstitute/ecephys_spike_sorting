from cookiecutter.main import cookiecutter as cc
import ruamel.yaml as yaml
import os

settings_fname = os.path.join(os.path.dirname(__file__), '.cookiecutter.yaml')
settings = yaml.safe_load(open(settings_fname, 'r'))['default_context']

cc(settings['_template'],
    output_dir="../..",
    config_file=".cookiecutter.yaml",
    no_input=True,
    overwrite_if_exists=True)
