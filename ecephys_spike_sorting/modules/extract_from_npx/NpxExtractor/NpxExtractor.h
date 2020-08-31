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


#ifndef __NEUROPIXTHREAD_H_2C4CBD67__
#define __NEUROPIXTHREAD_H_2C4CBD67__

#include "JuceHeader.h"
#include <stdio.h>
#include <string.h>

#include <Windows.h>

#include "npy-c++/NpyFile.h"

#pragma once

namespace Neuropix {

	class NpxExtractor 
	{

	public:

		NpxExtractor() { num_seconds = -1; }
		~NpxExtractor() { }

		bool setInputDirectory(File& file_);
		bool setOuputDirectory(File& file_);
		void createDirectory(File& file_);
		void setNumSeconds(int ns_);
		void convert();

	protected:

		virtual void createOutputFiles() { }

		virtual void readData() { }
		
		int counter;

		File input_directory;
		File output_directory;

		int num_seconds;

		struct ProbeInfo {

			ScopedPointer<NPY::NpyFile> timestampsAp;
			ScopedPointer<NPY::NpyFile> timestampsLfp;
			ScopedPointer<NPY::NpyFile> timestampsEvents;
			ScopedPointer<NPY::NpyFile> channelStates;

			ScopedPointer<FileOutputStream> apOutputStream;
			ScopedPointer<FileOutputStream> lfpOutputStream;

			String slotId;
			int8_t port;

			File npxFile;

			int64 timestamp;
			uint8_t eventCode;

		};

		OwnedArray<ProbeInfo> probeInfo;

	};

};
#endif  // __NEUROPIXTHREAD_H_2C4CBD67__
