
from ligotools import utils as ut
import numpy as np


def ntest_whiten():

	# Parameters
	eventname = 'GW150914'
	fnjson = _join_repo_path("BBH_events_v3.json", verbose=VERBOSE)
	events = json.load(open(fnjson,"r"))
	event = events[eventname]
	filename = event[f'fn_{file_code}']
	file_path = _join_repo_path(filename, verbose=VERBOSE)	
		
	# Load data
	strain_, time_, chan_dict_ = loaddata(file_path, file_code)
	
	# Remaining parameters
	fs = 4096
	NFFT = 4*fs
	Pxx_, freqs = mlab.psd(strain_, Fs=fs, NFFT=NFFT)
	psd_ = interp1d(freqs, Pxx_)
	dt = time_[1] - time_[0]
	
	strain_whiten = ut.whiten(strain_H1,psd_H1,dt)
	
	assert isinstance(strain_whiten, np.ndarray) and len(strain_whiten)>0
	
	
	
	