from argschema import ArgSchemaParser
import os
import logging
import time

from ecephys_spike_sorting.modules.noise_templates.id_noise_templates import id_noise_templates


def classify_noise_templates(args):

    logging.info('Running noise template identification')
    
    start = time.time()
    
     # LOTS OF HARD-CODED PARAMETERS IN HERE:
    templateIDs, is_noise = id_noise_templates(args['kilosort_output_directory'])
    
    execution_time = time.time() - start
    
    return {"execution_time" : execution_time} # output manifest


def main():

    from _schemas import InputParameters, OutputParameters

    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = classify_noise_templates(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
