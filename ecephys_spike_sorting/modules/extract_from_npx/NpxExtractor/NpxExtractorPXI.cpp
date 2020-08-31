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

#include "NpxExtractorPXI.h"

using namespace Neuropix;

#define NUM_CHANNELS 384
#define BUFFER_SIZE 1

void NpxExtractorPXI::createOutputFiles()
{
	input_directory.findChildFiles(npxFiles, 2, false, "recording*.npx2");

	std::cout << "Found " << npxFiles.size() << " npx files" << std::endl;

	for (int i = 0; i < npxFiles.size(); i++)
	{

		String filename = npxFiles[i].getFullPathName();

		std::cout << "File " << i << ": " << filename << std::endl;
		int slotStringIndex = filename.indexOf("slot");

		String slotId = filename.substring(slotStringIndex, slotStringIndex + 5);

		std::cout << " Slot ID: " << slotId << std::endl;

		//std::map<const int, ProbeInfo*> thisPortMap;

		for (int8_t port = 1; port < 4; port++) // loop through ports
		{
			np_streamhandle_t stream;

			NP_ErrorCode errorCode = streamOpenFile(filename.getCharPointer(), port, false, &stream);

			std::cout << "Searching for port " << int(port) << std::endl;

			errorCode = streamSetPos(stream, 0);

			uint32_t ts[1];
			ts[0] = 100;
			int16_t data[NUM_CHANNELS];

			int numRead = streamRead(
				stream,
				ts,
				data,
				1);


			if (numRead > 0)
			{

				ProbeInfo* info = new ProbeInfo();
				info->slotId = slotId;
				info->port = port;
				info->npxFile = npxFiles[i];
				std::cout << "  Found port " << int(port) << std::endl;
				info->timestamp = 0;
				info->eventCode = 0;

				bool foundMatch = false;
				for (int j = 0; j < probeInfo.size(); j++)
				{
					if (probeInfo[j]->port == port)
						foundMatch = true;
				}

				if (!foundMatch)
				{
					probeInfo.add(info);
					portMapping.insert(std::pair<const int, ProbeInfo*>(port, info));
				}
				

			}
			else {
				std::cout << "  Not found." << std::endl;
			}

			streamClose(stream);
		}

		//portMapping.push_back(thisPortMap);
	}

	if (true)
	{

		std::cout << "Creating output files" << std::endl;
		File continuous_directory = output_directory.getChildFile("continuous");
		createDirectory(continuous_directory);

		File events_directory = output_directory.getChildFile("events");
		createDirectory(events_directory);

		for (int i = 0; i < probeInfo.size(); i++)
		{

			ProbeInfo* info = probeInfo[i];

			String directoryName = "Neuropix-PXI-" + info->slotId + "-probe" + String(info->port);

			File ap_dir = continuous_directory.getChildFile(directoryName + "-AP");
			File lfp_dir = continuous_directory.getChildFile(directoryName + "-LFP");
			createDirectory(ap_dir);
			createDirectory(lfp_dir);

			File ap_dat_file = ap_dir.getChildFile("continuous.dat");
			File lfp_dat_file = lfp_dir.getChildFile("continuous.dat");
			File ap_timestamps_file = ap_dir.getChildFile("ap_timestamps.npy");
			File lfp_timestamps_file = lfp_dir.getChildFile("lfp_timestamps.npy");

			File ttl_dir1 = events_directory.getChildFile(directoryName);
			createDirectory(ttl_dir1);

			File ttl_dir2 = ttl_dir1.getChildFile("TTL_1");
			createDirectory(ttl_dir2);

			File event_timestamps_file = ttl_dir2.getChildFile("event_timestamps.npy");
			File channel_states_file = ttl_dir2.getChildFile("channel_states.npy");

			std::cout << "Created all directories." << std::endl;

			// create pointers for writing data

			info->timestampsAp = new NPY::NpyFile(ap_timestamps_file.getFullPathName(), NPY::NpyType(NPY::BaseType::INT64, 1));
			info->timestampsLfp = new NPY::NpyFile(lfp_timestamps_file.getFullPathName(), NPY::NpyType(NPY::BaseType::INT64, 1));

			info->timestampsEvents = new NPY::NpyFile(event_timestamps_file.getFullPathName(), NPY::NpyType(NPY::BaseType::INT64, 1));
			info->channelStates = new NPY::NpyFile(channel_states_file.getFullPathName(), NPY::NpyType(NPY::BaseType::INT16, 1));

			info->apOutputStream = new FileOutputStream(ap_dat_file);
			info->lfpOutputStream = new FileOutputStream(lfp_dat_file);

			std::cout << "Created file pointers" << std::endl;
		}
	}
}


void NpxExtractorPXI::readData()
{
	NP_ErrorCode errorCode;
	np_streamhandle_t stream;

	pckhdr_t header[BUFFER_SIZE];
	int16_t data[BUFFER_SIZE * NUM_CHANNELS];

	for (int i = 0; i < npxFiles.size(); i++)
	{

		int64 start_time = Time::currentTimeMillis();

		String filename = npxFiles[i].getFullPathName();

		std::cout << "Reading from " << filename << std::endl;

		errorCode = streamOpenFile(filename.getCharPointer(), 0, false, &stream);

		errorCode = streamSetPos(stream, 0);
		size_t numRead = 1;

		//std::cout << "Read LFP: " << read_lfp << std::endl;

		while (numRead > 0) // < 100)) // * 30000 || num_seconds == -1))
		{
			//uint64_t location = streamTell(stream);

			//std::cout << "Location in file: " << location << std::endl;

			errorCode = streamReadPacket(
				stream,
				header,
				data,
				NUM_CHANNELS,
				&numRead);

			//std::cout << "Num read: " << numRead << std::endl;

			if (numRead == NUM_CHANNELS)
			{
				uint8_t status = header->status;
				uint8_t sourceId = header->sourceid;

				int port = sourceId / 2 + 1;
				bool isLfp = sourceId % 2;
				//int slot = sourceId >> 3;

				//std::cout << "Port: " << port << ", isLfp: " << isLfp << std::endl;

				int64 ts = portMapping[port]->timestamp;
				uint8_t lastEventCode = portMapping[port]->eventCode;

				if (isLfp)
				{
					// assumes 250x gain
					for (int ch = 0; ch < NUM_CHANNELS; ch++)
					{
						data[ch] = int((float(data[ch]) * (1.2f / 1024.f)  / 250.0f * 1000000.0f) / 0.195f);
					}

					portMapping[port]->lfpOutputStream->write(data, NUM_CHANNELS * 2);
					portMapping[port]->timestampsLfp->writeData(&ts, sizeof(int64));
					portMapping[port]->timestampsLfp->increaseRecordCount(1);
				}
				else {

					// assumes 500x gain
					for (int ch = 0; ch < NUM_CHANNELS; ch++)
					{
						data[ch] = int((float(data[ch]) * (1.2f / 1024.f) / 500.0f * 1000000.0f) / 0.195f);
					}

					portMapping[port]->apOutputStream->write(data, NUM_CHANNELS * 2);
					portMapping[port]->timestampsAp->writeData(&ts, sizeof(int64));
					portMapping[port]->timestampsAp->increaseRecordCount(1);

					uint8_t thisEventCode = (header[0].status >> 6) & 1;

					
					//uint32_t current_timestamp = header[0].timestamp;

					//std::cout << current_timestamp << std::endl;

					//std::cout << "   Timestamp: " << current_timestamp << std::endl;

					//if (current_timestamp == headstage_timestamp)
					//{
					//	std::cout << "Found non-incrementing timestamps: " << current_timestamp << ", at sample number " << timestamp << ", source id: " << int(sourceId) << std::endl;
					//}

					//headstage_timestamp = current_timestamp;

					if (lastEventCode != thisEventCode)
					{
						for (int c = 0; c < 1; ++c)
						{
							if (((thisEventCode >> c) & 0x01) != ((lastEventCode >> c) & 0x01))
							{
								portMapping[port]->timestampsEvents->writeData(&ts, sizeof(int64));
								portMapping[port]->timestampsEvents->increaseRecordCount(1);

								int16 channelState;

								if ((thisEventCode >> c) & 0x01)
								{
									channelState = (c + 1);
								}
								else {
									channelState = (c + 1)*-1;
								}

								portMapping[port]->channelStates->writeData(&channelState, sizeof(int16));
								portMapping[port]->channelStates->increaseRecordCount(1);

								//std::cout << "Wrote event data." << std::endl;
							} // eventCode
						} // check event channels
					} // new eventCode	

					portMapping[port]->eventCode = thisEventCode;
					portMapping[port]->timestamp += 1;

				} // read AP vs read LFP
			}
			else { // not 384 samples

				//std::cout << "Wrong number of samples found." << std::endl;
			}
		} // while numRead > 0

		int64 end_time = Time::currentTimeMillis();
		float total_time = float(end_time - start_time) / 1000.0f;
		float ratio;
		//if (num_seconds > 0)
		//	ratio = float(num_seconds) / total_time;

		std::cout << "Total processing time: " << total_time << " seconds " << std::endl;
		//std::cout << ratio << "x real time" << std::endl;

	} // loop through probes


}

