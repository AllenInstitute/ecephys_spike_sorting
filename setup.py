from setuptools import setup, find_packages

setup(
    name = 'ecephys_spike_sorting',
    version = '0.1.0',
    description = """Tools for spike-sorting Allen Insitute Neuropixels data""",
    author = "josh siegle",
    author_email = "joshs@alleninstitute.org",
    url = 'https://github.com/AllenInstitute/ecephys_spike_sorting',
    packages = find_packages(),
    include_package_data=True,
    entry_points={
          'console_scripts': [
              'ecephys_spike_sorting = ecephys_spike_sorting.__main__:main'
        ]
    },
    setup_requires=['pytest-runner'],
)
