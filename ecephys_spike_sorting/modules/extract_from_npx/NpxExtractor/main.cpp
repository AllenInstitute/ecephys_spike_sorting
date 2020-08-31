// NpxExtractor.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <iostream> 
#include <stdlib.h>

#include "NpxExtractorPXI.h"
#include "NpxExtractor3a.h"
#include "JuceHeader.h"

#include <Windows.h>

#define NPXv1 0
#define NPXv2 1

int main(int argc, char* argv[])
{

	const char* input_directory_name;
	const char* output_directory_name;
	const char* num_seconds_string;

	int fileType;

	int32 num_seconds = -1;

	if (argc == 3 || argc == 4)
	{
		input_directory_name = argv[1];
		output_directory_name = argv[2];
		std::cout << "input directory: " << input_directory_name << std::endl;
		std::cout << "output directory: " << output_directory_name << std::endl;

		if (argc == 4)
		{
			num_seconds_string = argv[3];
			std::cout << "seconds to convert: " << num_seconds_string << std::endl;
			String ns = String(num_seconds_string);
			num_seconds = ns.getIntValue();
		}
	}
	else {
		std::cout << "Wrong number of input arguments (2 or 3 required)" << std::endl;
		return -1;
	}

	String fname = String(input_directory_name);
	File input_directory(fname);

	if (!input_directory.isDirectory())
	{
		std::cout << "First input argument is not a directory." << std::endl;
		return -1;
	}
	else {
		
		Array<File> results;
		input_directory.findChildFiles(results, 2, false, "recording*.npx");
		fileType = NPXv1;

		if (results.size() < 1)
		{
			
			input_directory.findChildFiles(results, 2, false, "recording*.npx2");
			fileType = NPXv2;

			if (results.size() < 1)
			{
				std::cout << "Found no NPX v1 or NPX v2" << std::endl;
				return -1;
			}
			else {
				std::cout << "Found NPX v2" << std::endl;
			}
		}
		else {
			std::cout << "Found NPX v1" << std::endl;
		}
	}

	fname = String(output_directory_name);
	File output_directory(fname);

	std::cout << "Creating npx converter." << std::endl;

	ScopedPointer<Neuropix::NpxExtractor> neuropix;

	if (fileType == NPXv1)
		neuropix = new Neuropix::NpxExtractor3a();
	else
		neuropix = new Neuropix::NpxExtractorPXI();

	if (!neuropix->setInputDirectory(input_directory))
	{
		std::cout << "Input directory does not exist." << std::endl;
		return -1;
	}

	if (!neuropix->setOuputDirectory(output_directory))
	{
		std::cout << "Output directory does not exist." << std::endl;
		return -1;
	}

	neuropix->setNumSeconds(num_seconds);

	std::cout << "Starting conversion." << std::endl;

	neuropix->convert();

	std::cout << "Conversion finished." << std::endl;

	return 0;
}