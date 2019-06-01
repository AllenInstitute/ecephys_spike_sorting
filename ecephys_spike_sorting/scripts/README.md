# Batch Processing Scripts

Each module can be run on its own using the following syntax:

```
python -m ecephys_spike_sorting.modules.<module name> --input_json <path to input json> --output_json <path to output json>
```

However, you'll typically want to run several modules in order, iterating over multiple sets of input files. These scripts provide examples of how to implement batch processing, as well as a way to auto-generate the input JSON files containing module parameters.

## Getting Started

The first thing you'll want to do