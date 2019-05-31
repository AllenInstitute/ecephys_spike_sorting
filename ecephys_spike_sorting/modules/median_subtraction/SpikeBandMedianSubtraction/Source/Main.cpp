/*
  ==============================================================================

    SpikeBandMedianSubtraction
    (c) 2017 Allen Institute for Brain Science

    written by joshs@alleninstitute.org

  ==============================================================================
*/

// VERSION 0.1 //

#include "../JuceLibraryCode/JuceHeader.h"
#include <stdio.h>
#include <stdlib.h>
#include <algorithm>

//==============================================================================
int compare (const void * a, const void * b)
{
  return ( *(int16_t*)a - *(int16_t*)b );
}

int main (int argc, char* argv[])
{

	Array<int> offset;
	Array<float> scaling;
	Array<bool> mask;

    const char* json_file_name;
	const char* data_file_name;
	int max_channel;

	if (argc == 4)
	{
		json_file_name = argv[1];
		data_file_name = argv[2];
		max_channel = String(argv[3]).getIntValue();
		std::cout << "json file: " << json_file_name << std::endl;
		std::cout << "data file: " << data_file_name << std::endl;
		std::cout << "max channel: " << max_channel << std::endl;
	} else {
		std::cout << argc << std::endl;
		std::cerr << "Not enough input arguments." << std::endl;
		return 1;
	}

	std::cout << "Creating input files..." << std::endl;
	String fname1 = String(json_file_name);
	File json_file(fname1);

	String fname2 = String(data_file_name);
	File data_file(fname2);

	File residuals_file = data_file.getParentDirectory().getChildFile("residuals.dat");

	// parse JSON file:
	std::cout << "Reading JSON file..." << std::endl;
	FileInputStream jsonInputStream(json_file);

    var json = JSON::parse(jsonInputStream);

	std::cout << "   scaling" << std::endl;
    var s = json[Identifier("scaling")];
    Array<var>* j_scaling = s.getArray();

	std::cout << "   mask" << std::endl;
    var m = json[Identifier("mask")];
    Array<var>* j_mask = m.getArray();

	std::cout << "   channels" << std::endl;
    var c = json[Identifier("channel")];
    Array<var>* j_channels = c.getArray();
	
	std::cout << "   offset" << std::endl;
    var o = json[Identifier("offset")];
    Array<var>* j_offset = o.getArray();

    for (int i = 0; i < 384; i++)
    {
		//std::cout << "Reading offset " << i <<  std::endl;
    	offset.add(j_offset->getUnchecked(i));
    	scaling.add(j_scaling->getUnchecked(i));
    	mask.add(j_mask->getUnchecked(i));
    }

    //std::cout << mask[0] << std::endl;
    //std::cout << scaling[0] << std::endl;
    //std::cout << offset[0] << std::endl;

    // read in DAT file:
	std::cout << "Creating file input and output streams" << std::endl;
    FileInputStream dataInputStream(data_file);
    FileOutputStream dataOutputStream(data_file);
	FileOutputStream residualsOutputStream(residuals_file);

    const uint64 total_channels = 384;
    const uint64 buffer_samples = 1;
    const int sample_rate = 30000;

    int16_t input_buffer [total_channels * buffer_samples];
    int16_t offset_subtr [total_channels];
    int16_t median_buffer[total_channels];
	int16_t residuals_buffer[24];
    int16_t output_buffer [total_channels * buffer_samples];

    std::cout << "File size in bytes: " << dataInputStream.getTotalLength() << std::endl;
	std::cout << "File size in samples: " << dataInputStream.getTotalLength()  / total_channels / 2 << std::endl;
	std::cout << "File size in seconds: " << dataInputStream.getTotalLength()  / total_channels / 2 / sample_rate << std::endl;

	int64 totalIter = (int64) dataInputStream.getTotalLength() / total_channels / 2 / buffer_samples;

    int64 start_time = Time::currentTimeMillis();

	int count = 0;

    for (int64 iter = 0; iter < totalIter; iter++)
    {
		int64 position = iter * total_channels * 2 * buffer_samples;
		//if (count < 30000)
		//{
		//	count++;
		//}
		//else {
		//	std::cout << position << std::endl;
		//	count = 0;
		//}
			
		int numBytes = total_channels * 2 * buffer_samples;
		int numBytesResiduals = 24 * 2 * buffer_samples;

    	dataInputStream.setPosition(position);
		int numRead = dataInputStream.read(input_buffer, numBytes);
 
 		// loop through buffer samples (if > 1)
		for (int sample = 0; sample < buffer_samples; sample++)
		{
			// offset subtraction
			for (int i = 0; i < max_channel; i++)
			{
				offset_subtr[i] = input_buffer[sample * total_channels + i] - offset[i];
			}

			// median subtraction

			for (int i = 0; i < 24; i++)
			{
				int idx = -1;

				for (int ch = i; ch < max_channel; ch += 24)
				{
					if (mask[ch])
					{
						idx++;
						median_buffer[idx] = offset_subtr[ch];
					}
				}

				std::sort(median_buffer, median_buffer + idx);
				residuals_buffer[i] = median_buffer[idx / 2];
			}

			for (int i = 0; i < total_channels; i++)
			{
				if (i < max_channel)
					output_buffer[sample * total_channels + i] = offset_subtr[i] - int(float(residuals_buffer[i % 24]) * scaling[i]);
				else
					output_buffer[sample * total_channels + i] = input_buffer[sample * total_channels + i];
			}
    	}

    	// write to file
		dataOutputStream.setPosition(position);
		dataOutputStream.write(output_buffer, numBytes);
		residualsOutputStream.write(residuals_buffer, numBytesResiduals);
		
    }

    int64 end_time = Time::currentTimeMillis();

    std::cout << "Total processing time: " << (end_time - start_time)/1000 << " seconds " << std::endl;

    return 0;
}
