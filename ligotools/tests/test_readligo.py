import os
import pytest
import numpy as np
from ligotools import readligo as rl 
from ligotools.tests import conftest as cf



@pytest.mark.parametrize('file_code', ['H1', 'L1'])
def test_read_hdf5(file_code):
	
	filename = f"{file_code[0]}-{file_code}_LOSC_4_V2-1126259446-32.hdf5"
	file_path = cf.join_data_path(filename)
	strain, gpsStart, ts, qmask, shortnameList, injmask, injnameList = rl.read_hdf5(file_path)
	
	assert isinstance(strain, np.ndarray) and len(strain)>0
	assert isinstance(gpsStart, np.int64)
	assert isinstance(ts, np.float64)
	assert isinstance(qmask, np.ndarray) and len(qmask)>0
	assert isinstance(shortnameList, list) and len(shortnameList)>0
	assert isinstance(injmask, np.ndarray) and len(injmask)>0
	assert isinstance(injnameList, list) and len(injnameList)>0


@pytest.mark.parametrize('file_code', ['H1', 'L1'])
def test_loaddata(various_ligotools_objects):
	
	# strain_time_chan is a fixture with the result of loaddata
	# It is defined in conftest.py
	event, strain, time, chan_dict, fs, NFFT, freqs, dt, strain_whiten = various_ligotools_objects
	
	# Validations
	assert isinstance(strain, np.ndarray)
	assert len(strain) > 0
	assert isinstance(chan_dict, dict)
	assert len(chan_dict) > 0
	for val in chan_dict.values():
		assert isinstance(val, np.ndarray)
		assert len(val) > 0

def test_filelist():
	file_list = rl.FileList(cf.data_path())
	file_paths = file_list.searchdir(file_list.directory)
	assert file_list.directory == cf.data_path()
	assert len(file_paths) > 0
