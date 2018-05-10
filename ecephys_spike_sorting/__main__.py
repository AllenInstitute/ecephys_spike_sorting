from ._schemas import InputParameters, OutputParameters
from argschema import ArgSchemaParser
import argparse

from . import __version__

class ArgSchemaParserPlus(ArgSchemaParser):
    
    def __init__(self,*args,**kwargs):

        parser = argparse.ArgumentParser() 
        parser.add_argument('--version', action='version', version=__version__)
        [known_args, extra_args] = parser.parse_known_args()
        self.args = known_args 

        super(ArgSchemaParserPlus,self).__init__(args=extra_args, **kwargs)


def main():

    """Main entry point:"""
    mod = ArgSchemaParserPlus(schema_type=InputParameters,
                              output_schema_type=OutputParameters)

    output = {}
    # YOUR STUFF GOES HERE
    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output)
    else:
        print(mod.get_output_json(output))

    

if __name__ == "__main__":
    main()