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

#include "NpxExtractor.h"

#include <direct.h>

using namespace Neuropix;

bool NpxExtractor::setInputDirectory(File& file_)
{
	if (file_.exists())
	{
		input_directory = file_;
		return true;
	}
	else {
		return false;
	}
}

bool NpxExtractor::setOuputDirectory(File& file_)
{
	if (file_.exists())
	{
		output_directory = file_;
		return true;
	}
	else {
		return false;
	}
}

void NpxExtractor::setNumSeconds(int ns_)
{
	num_seconds = ns_;
}

void NpxExtractor::convert()
{
	createOutputFiles();
	readData();
}

void NpxExtractor::createDirectory(File& file)
{
	_mkdir(file.getFullPathName().getCharPointer());
}

