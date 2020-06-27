from setuptools import setup, find_packages

setup(
    name = 'ecephys_spike_sorting',
    version = '0.1.0',
    description = """Tools for spike-sorting Allen Institute Neuropixels data""",
    author = "Josh Siegle, Nile Graddis, Xiaoxuan Jia, Gregg Heller, Chris Mochizuki, Dan Denman",
    author_email = "joshs@alleninstitute.org",
    url = 'https://github.com/AllenInstitute/ecephys_spike_sorting',
    packages = find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
              'automerging = ecephys_spike_sorting.modules.automerging.__main__:main',
              'depth-estimation = ecephys_spike_sorting.modules.depth_estimation.__main__:main',
              'extract-from-npx = ecephys_spike_sorting.modules.extract_from_npx.__main__:main',
              'kilosort-helper = ecephys_spike_sorting.modules.kilosort_helper.__main__:main',
              'kilosort-postprocessing = ecephys_spike_sorting.modules.kilosort_postprocessing.__main__:main',
              'mean-waveforms = ecephys_spike_sorting.modules.mean_waveforms.__main__:main',
              'median-subtraction = ecephys_spike_sorting.modules.median_subtraction.__main__:main',
              'noise-templates = ecephys_spike_sorting.modules.noise_templates.__main__:main',
              'quality-metrics = ecephys_spike_sorting.modules.quality_metrics.__main__:main',
        ],
    },
    setup_requires=['pytest-runner'],
    install_requires=[
        'matplotlib',
        'scipy',
        'numpy',
        'pandas',
        'GitPython',
        'pillow',
        'argschema',
        'xmljson',
        'xarray',
        'scikit-learn',
        'joblib'
    ],
)
