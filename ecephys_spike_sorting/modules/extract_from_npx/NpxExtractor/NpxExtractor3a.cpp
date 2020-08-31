/*
------------------------------------------------------------------

This file is part of the Open Ephys GUI
Copyright (C) 2017 Allen Institute for Brain Science and Open Ephys

------------------------------------------------------------------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/

#include "NpxExtractor3a.h"

using namespace Neuropix;


void NpxExtractor3a::createOutputFiles()
{

	probeInfo.add(new ProbeInfo());

	std::cout << "Creating output files" << std::endl;
	File continuous_directory = output_directory.getChildFile("continuous");
	createDirectory(continuous_directory);

	File ap_dir = continuous_directory.getChildFile("Neuropix-3a-100.0");
	File lfp_dir = continuous_directory.getChildFile("Neuropix-3a-100.1");
	createDirectory(ap_dir);
	createDirectory(lfp_dir);

	File ap_dat_file = ap_dir.getChildFile("continuous.dat");
	File lfp_dat_file = lfp_dir.getChildFile("continuous.dat");
	File ap_timestamps_file = ap_dir.getChildFile("ap_timestamps.npy");
	File lfp_timestamps_file = lfp_dir.getChildFile("lfp_timestamps.npy");

	// set up output streams: event data
	File events_directory = output_directory.getChildFile("events");
	createDirectory(events_directory);

	File ttl_dir1 = events_directory.getChildFile("Neuropix-3a-100.0");
	createDirectory(ttl_dir1);

	File ttl_dir2 = ttl_dir1.getChildFile("TTL_1");
	createDirectory(ttl_dir2);

	File event_timestamps_file = ttl_dir2.getChildFile("event_timestamps.npy");
	File channel_states_file = ttl_dir2.getChildFile("channel_states.npy");

	// create pointers for writing data
	std::cout << "Created all directories." << std::endl;

	probeInfo[0]->timestampsAp = new NPY::NpyFile(ap_timestamps_file.getFullPathName(), NPY::NpyType(NPY::BaseType::INT64, 1));
	probeInfo[0]->timestampsLfp = new NPY::NpyFile(lfp_timestamps_file.getFullPathName(), NPY::NpyType(NPY::BaseType::INT64, 1));

	probeInfo[0]->timestampsEvents = new NPY::NpyFile(event_timestamps_file.getFullPathName(), NPY::NpyType(NPY::BaseType::INT64, 1));
	probeInfo[0]->channelStates = new NPY::NpyFile(channel_states_file.getFullPathName(), NPY::NpyType(NPY::BaseType::INT16, 1));

	probeInfo[0]->apOutputStream = new FileOutputStream(ap_dat_file);
	probeInfo[0]->lfpOutputStream = new FileOutputStream(lfp_dat_file);

	std::cout << "Created file pointers" << std::endl;
}



// PACKET CONTENTS:
// 01 - XXXXXXXXX - 4-bit lfp ctr - 1-bit start - 16-bit sync
// 11 - XXXXXXXXXX - MSB ctr0 - LSB ctr0
// 00 - lfp2 - lfp1 - lfp0
//     ...
// 00 - XXXXXXXXXX - lfp31 - lfp30
// 11 - XXXXXXXXXX - MSB ctr1 - LSB ctr1
//     ...
// 11 - XXXXXXXXXX - MSB ctr12 - LSB ctr12
// 00 - AP2 - AP1 - AP0
//     ...
// 00 - AP383 - AP382 - AP381

void NpxExtractor3a::readData()
{

	Array<File> npxFiles;

	input_directory.findChildFiles(npxFiles, 2, false, "recording*.npx");

	std::cout << "Found " << npxFiles.size() << " npx files" << std::endl;

	Array<int> fileNumbers;
	Array<int> fileIndices;

	std::cout << "Searching for file numbers..." << std::endl;
	for (int i = 0; i < npxFiles.size(); i++)
	{
		String filename = npxFiles[i].getFileNameWithoutExtension();
		String digits = filename.substring(9);
		fileNumbers.add(digits.getIntValue());
		std::cout << digits.getIntValue() << " ";
	}
	std::cout << std::endl;

	std::cout << "Sorting file numbers..." << std::endl;
	for (int i = 0; i < fileNumbers.size(); i++)
	{
		int index = 0;
		for (int j = 0; j < fileNumbers.size(); j++)
		{
			if (fileNumbers[i] > fileNumbers[j])
			{
				index += 1;
			}
		}
		fileIndices.add(index);
		std::cout << index << " ";
	}
	std::cout << std::endl;

	std::cout << "Converting..." << std::endl;

	const int total_channels = 384;

	uint16 lastEventCode = -1;
	int64 timestamp = 0;

	bool stopWriting = false;

	for (int i = 0; i < npxFiles.size(); i++)
	{
		int64 start_time = Time::currentTimeMillis();

		std::cout << npxFiles[fileIndices.indexOf(i)].getFileName() << std::endl;

		// write a zero to indicate start of new file
		std::cout << "Writing split file event" << std::endl;
		probeInfo[0]->timestampsEvents->writeData(&timestamp, sizeof(int64));
		probeInfo[0]->timestampsEvents->increaseRecordCount(1);
		int16 fileStartCode = 0;
		probeInfo[0]->channelStates->writeData(&fileStartCode, sizeof(int16));
		probeInfo[0]->channelStates->increaseRecordCount(1);

		std::cout << "Creating input stream" << std::endl;
		FileInputStream npxfile(npxFiles[fileIndices.indexOf(i)]);

		uint64 length_in_bytes = npxfile.getTotalLength();
		uint64 length_in_samples = length_in_bytes / PACKET_SIZE;
		uint64 length_in_blocks = length_in_samples / 12;
		float length_in_seconds = float(length_in_samples) / 30000.0f;

		std::cout << "Total file size: " << length_in_seconds << " seconds " << std::endl;

		if (num_seconds > 0)
		{
			std::cout << "Length to convert: " << num_seconds << " seconds " << std::endl;
			length_in_blocks = 2500 * num_seconds;
		}

		for (uint64 block = 0; block < length_in_blocks; block++) // 
		{

			int16 ap_data[12][total_channels];
			int16 lfp_data[total_channels];
			uint16 eventCode[12];
			uint64 counter_data[12][13];

			int16 lfp_packet_num;

			for (int P = 0; P < 12; P++)
			{
				if (!stopWriting)
				{
					uint32 packet[153];

					npxfile.read(packet, PACKET_SIZE);

					int counter_idx = 0;
					int lfp_sample_idx = 0;
					int ap_sample_idx = 0;

					for (int p_num = 0; p_num < 153; p_num++)
					{
						uint8 sp[4];
						uint8 reordered[4];
						memcpy(sp, &packet[p_num], 4);

						reordered[0] = sp[3];
						reordered[1] = sp[2];
						reordered[2] = sp[1];
						reordered[3] = sp[0];

						uint32 subpacket;
						memcpy(&subpacket, reordered, 4);

						uint32 start_code = (subpacket >> 30);

						if (start_code == 1) // first line
						{
							eventCode[P] = subpacket & 65535;
							lfp_packet_num = (subpacket >> 17) & 15;
							//std::cout << lfp_packet_num << std::endl;
							//std::cout << eventCode[P] << std::endl;
						}
						else if (start_code == 3) // counters
						{
							counter_data[P][counter_idx] = (subpacket)& 1048575;
							counter_idx++;
						}
						else if (start_code == 0) // data
						{
							if (p_num < 13) // lfp
							{
								for (int s = 0; s < 3; s++)
								{
									if (lfp_sample_idx < 32)
									{
										int16 this_sample = ((subpacket >> (10 * s)) & 1023);
										lfp_data[lfp_sample_idx * 12 + lfp_packet_num] = int(((float(this_sample) * (1.2f / 1024.f) - 0.6f) / 250.0f * -1000000.0f) / 0.195f);
										lfp_sample_idx++;
									}
									else {
										lfp_sample_idx = 0;
									}

								}
							}
							else {
								for (int s = 0; s < 3; s++)
								{
									int16 this_sample = ((subpacket >> (10 * s)) & 1023);
									//jassert(ap_sample_idx < 384);
									if (ap_sample_idx < 384)
									{
										ap_data[P][ap_sample_idx] = int(((float(this_sample) * (1.2f / 1024.f) - 0.6f) / 500.0f * -1000000.0f) / 0.195f);
										ap_sample_idx++;
									}
									else {
										std::cout << "Corrupted data at timestamp " << timestamp << std::endl;
										stopWriting = true;
									}

								}
							}
						}
					} // subpackets (32 bits)

				}
				else {
					break;
				}

			} // packet (153 sub-packets)

			if (!stopWriting)
			{
				for (int P = 0; P < 12; P++)
				{
					probeInfo[0]->apOutputStream->write(ap_data[P], total_channels * 2);
					probeInfo[0]->timestampsAp->writeData(&timestamp, sizeof(int64));
					probeInfo[0]->timestampsAp->increaseRecordCount(1);

					if (P == 0)
					{
						probeInfo[0]->lfpOutputStream->write(lfp_data, total_channels * 2);
						probeInfo[0]->timestampsLfp->writeData(&timestamp, sizeof(int64));
						probeInfo[0]->timestampsLfp->increaseRecordCount(1);
					}

					if (timestamp > 0)
					{
						if (lastEventCode != eventCode[P])
						{
							for (int c = 0; c < 16; ++c)
							{
								if (((eventCode[P] >> c) & 0x01) != ((lastEventCode >> c) & 0x01))
								{
									probeInfo[0]->timestampsEvents->writeData(&timestamp, sizeof(int64));
									probeInfo[0]->timestampsEvents->increaseRecordCount(1);

									int16 channelState;

									if ((eventCode[P] >> c) & 0x01)
									{
										channelState = (c + 1);
									}
									else {
										channelState = (c + 1)*-1;
									}

									probeInfo[0]->channelStates->writeData(&channelState, sizeof(int16));
									probeInfo[0]->channelStates->increaseRecordCount(1);
								}
							}
						}
					}

					lastEventCode = eventCode[P];
					timestamp++;
				}
			}

		} // block (12 packets)

		int64 end_time = Time::currentTimeMillis();
		float total_time = float(end_time - start_time) / 1000.0f;
		float ratio;
		if (num_seconds > 0)
			ratio = float(num_seconds) / total_time;
		else
			ratio = length_in_seconds / total_time;

		std::cout << "Total processing time: " << total_time << " seconds " << std::endl;
		std::cout << ratio << "x real time" << std::endl;

		stopWriting = false;

	} // npx file
}

