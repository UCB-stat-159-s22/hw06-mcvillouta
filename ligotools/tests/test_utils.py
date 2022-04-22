
import os
import json
import pytest
import h5py
import numpy as np
import matplotlib.mlab as mlab
from scipy import signal
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt, iirdesign, zpk2tf, freqz

from ligotools import readligo as rl
from ligotools import utils as ut
from ligotools.tests import conftest as cf


@pytest.mark.parametrize('file_code', ['H1', 'L1'])
def test_whiten(various_ligotools_objects):
	
	event, strain, time, chan_dict, fs, NFFT, freqs, dt, strain_whiten = various_ligotools_objects
	
	assert isinstance(strain_whiten, np.ndarray) and len(strain_whiten)>0
	assert isinstance(freqs, np.ndarray) and len(freqs)>0
	assert isinstance(dt, np.float64) and dt>0


@pytest.mark.parametrize('file_code', ['H1', 'L1'])
def test_make_figures(various_ligotools_objects, file_code):
	
	# Various ligotools objects
	event, strain, time, chan_dict, fs, NFFT, freqs, dt, strain_whiten = various_ligotools_objects
	
	# More inputs needed
	fband = event['fband']
	tevent = event['tevent']
	fn_template = os.path.join(cf.data_path(), event['fn_template'])
	f_template = h5py.File(fn_template, "r")
	template_p, template_c = f_template["template"][...]
	template_offset = 16.
	plottype = "png"
	bb, ab = butter(4, [fband[0]*2./fs, fband[1]*2./fs], btype='band')
	normalization = np.sqrt((fband[1]-fband[0])/(fs/2))
	strain_whitenbp = filtfilt(bb, ab, strain_whiten) / normalization
	psd_window = np.blackman(NFFT)
	NOVL = NFFT/2
	template = (template_p + template_c*1.j) 
	etime = time+template_offset
	datafreq = np.fft.fftfreq(template.size)*fs
	df = np.abs(datafreq[1] - datafreq[0])

	try:
		dwindow = signal.tukey(template.size, alpha=1./8)
	except: 
		dwindow = signal.blackman(template.size)

	template_fft = np.fft.fft(template*dwindow) / fs
	data = strain
	det = file_code

	# -- Calculate the PSD of the data.  Also use an overlap, and window:
	data_psd, freqs = mlab.psd(data, Fs=fs, NFFT=NFFT, window=psd_window, noverlap=NOVL)

	# Take the Fourier Transform (FFT) of the data and the template (with dwindow)
	data_fft = np.fft.fft(data*dwindow) / fs

	# -- Interpolate to get the PSD values at the needed frequencies
	power_vec = np.interp(np.abs(datafreq), freqs, data_psd)

	# -- Calculate the matched filter output in the time domain:
	optimal = data_fft * template_fft.conjugate() / power_vec
	optimal_time = 2*np.fft.ifft(optimal)*fs

	# -- Normalize the matched filter output:
	sigmasq = 1*(template_fft * template_fft.conjugate() / power_vec).sum() * df
	sigma = np.sqrt(np.abs(sigmasq))
	SNR_complex = optimal_time/sigma

	# shift the SNR vector by the template length so that the peak is at the END of the template
	peaksample = int(data.size / 2)
	SNR_complex = np.roll(SNR_complex, peaksample)
	SNR = abs(SNR_complex)

	# find the time and SNR value at maximum:
	indmax = np.argmax(SNR)
	timemax = time[indmax]
	SNRmax = SNR[indmax]

	# Calculate the "effective distance" (see FINDCHIRP paper for definition)
	d_eff = sigma / SNRmax
	# -- Calculate optimal horizon distnace
	horizon = sigma/8

	# Extract time offset and phase at peak
	phase = np.angle(SNR_complex[indmax])
	offset = (indmax-peaksample)

	# apply time offset, phase, and d_eff to template 
	template_phaseshifted = np.real(template*np.exp(1j*phase))    # phase shift the template
	template_rolled = np.roll(template_phaseshifted,offset) / d_eff  # Apply time offset and scale amplitude

	# Whiten and band-pass the template for plotting
	template_whitened = ut.whiten(template_rolled, interp1d(freqs, data_psd), dt)  # whiten the template
	template_match = filtfilt(bb, ab, template_whitened) / normalization # Band-pass the template

	# plotting changes for the detectors:
	if det == 'L1': 
		pcolor='g'
	else:
		pcolor='r'
	
	ut.make_figures(
		time, 
		timemax, 
		SNR, 
		pcolor, 
		det, 
		tevent, 
		strain_whitenbp, 
		template_match, 
		template_fft, 
		datafreq, 
		d_eff, 
		freqs, 
		data_psd, 
		fs, 
		plottype
	)
	
	figures_path = os.path.join(cf.repo_path(), "figures")
	fn_plot1 = os.path.join(figures_path, f"eventname_{file_code}_SNR.{plottype}")
	fn_plot2 = os.path.join(figures_path, f"eventname_{file_code}_matchtime.{plottype}")
	fn_plot3 = os.path.join(figures_path, f"eventname_{file_code}_matchfreq.{plottype}")

	assert os.path.isfile(fn_plot1)
	assert os.path.isfile(fn_plot1)
	assert os.path.isfile(fn_plot1)
	
	# Clean up
	os.remove(fn_plot1)
	os.remove(fn_plot2)
	os.remove(fn_plot3)
	