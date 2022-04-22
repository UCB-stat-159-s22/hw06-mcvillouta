
import os
import pytest
import json
import matplotlib.mlab as mlab
from scipy.interpolate import interp1d
from ligotools import readligo as rl
from ligotools import utils as ut

VERBOSE = 1

def repo_path():
	return os.getcwd()

def data_path():
	path = os.path.join(repo_path(), "data")
	return path

def join_data_path(filename):
	data_path_str = data_path()
	file_path = os.path.join(data_path_str, filename)
	if VERBOSE:
		print(f"Current path: {os.getcwd()}")
		print(f"Repo path: {data_path_str}")
		print(f"File path: {file_path}")
	return file_path

@pytest.fixture
def various_ligotools_objects(file_code):
	"""
		request.param in ['H1', 'L1']
	"""
	
	# Parameters
	eventname = 'GW150914'
	fnjson = join_data_path("BBH_events_v3.json")
	events = json.load(open(fnjson,"r"))
	event = events[eventname]
	filename = event[f'fn_{file_code}']
	file_path = join_data_path(filename)	
		
	# Load data
	strain, time, chan_dict = rl.loaddata(file_path, file_code)
	
	# Remaining parameters
	fs = 4096
	NFFT = 4*fs
	Pxx, freqs = mlab.psd(strain, Fs=fs, NFFT=NFFT)
	psd = interp1d(freqs, Pxx)
	dt = time[1] - time[0]
	
	# Call whiten
	strain_whiten = ut.whiten(strain, psd, dt)
	
	return event, strain, time, chan_dict, fs, NFFT, freqs, dt, strain_whiten

