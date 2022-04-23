
import os
import pytest
import json
import h5py
import numpy as np
import matplotlib.mlab as mlab
from scipy import signal
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt, iirdesign, zpk2tf, freqz
from ligotools import readligo as rl
from ligotools import utils as ut


def repo_path():
	return os.getcwd()


def data_path():
	path = os.path.join(repo_path(), "data")
	return path


def join_data_path(filename):
	data_path_str = data_path()
	file_path = os.path.join(data_path_str, filename)
	return file_path


def get_figures_path(file_code):
	figures_path = os.path.join(repo_path(), "figures")
	fn_plot1 = os.path.join(figures_path, f"eventname_{file_code}_SNR.png")
	fn_plot2 = os.path.join(figures_path, f"eventname_{file_code}_matchtime.png")
	fn_plot3 = os.path.join(figures_path, f"eventname_{file_code}_matchfreq.png")
	return fn_plot1, fn_plot2, fn_plot3


def get_wav_path(file_code):
	wav_path = f"audio/eventname_{file_code}_whitenbp.wav"	
	return wav_path


@pytest.fixture
def get_various_ligotools_objects():
	# Using this fixture as factory
	
	# Pre-compute event
	eventname = 'GW150914'
	fnjson = join_data_path("BBH_events_v3.json")
	events = json.load(open(fnjson,"r"))
	event = events[eventname]
	
	# Function to load data
	def _get_various_ligotools_objects(file_code):
		"""
			file_code in ['H1', 'L1']
		"""
		filename = event[f'fn_{file_code}']
		file_path = join_data_path(filename)	

		# Load data
		strain, time, chan_dict = rl.loaddata(file_path, file_code)
		loaddata_objects = (event, strain, time, chan_dict)

		# Remaining parameters
		fs = 4096
		NFFT = 4*fs
		Pxx, freqs = mlab.psd(strain, Fs=fs, NFFT=NFFT)
		psd = interp1d(freqs, Pxx)
		dt = time[1] - time[0]

		# Call whiten
		strain_whiten = ut.whiten(strain, psd, dt)
		whiten_objects = (fs, NFFT, freqs, dt, strain_whiten)
	
		# Inputs for plots
		fband = event['fband']
		fn_template = os.path.join(data_path(), event['fn_template'])
		f_template = h5py.File(fn_template, "r")
		template_p, template_c = f_template["template"][...]
		template_offset = 16.
		bb, ab = butter(4, [fband[0]*2./fs, fband[1]*2./fs], btype='band')
		normalization = np.sqrt((fband[1]-fband[0])/(fs/2))
		strain_whitenbp = filtfilt(bb, ab, strain_whiten) / normalization	
		template = (template_p + template_c*1.j) 
		plot_objects = (bb, ab, normalization, strain_whitenbp, template)
	
		return loaddata_objects, whiten_objects, plot_objects
	
	return _get_various_ligotools_objects


@pytest.fixture
def build_figures(get_various_ligotools_objects, file_code):
	
	# Various ligotools objects
	loaddata_objects, whiten_objects, plot_objects = get_various_ligotools_objects(file_code)
	event, strain, time, chan_dic = loaddata_objects
	fs, NFFT, freqs, dt, strain_whiten = whiten_objects
	bb, ab, normalization, strain_whitenbp, template = plot_objects
	
	# More inputs needed
	tevent = event['tevent']
	psd_window = np.blackman(NFFT)
	NOVL = NFFT/2
	#etime = time+template_offset
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
		"png"
	)
	
	yield
	
	fn_plot1, fn_plot2, fn_plot3 = get_figures_path(file_code)
	
	# Clean up
	os.remove(fn_plot1)
	os.remove(fn_plot2)
	os.remove(fn_plot3)


@pytest.fixture
def build_wavfile(get_various_ligotools_objects, file_code):
	
	# Various ligotools objects
	loaddata_objects, whiten_objects, plot_objects = get_various_ligotools_objects(file_code)
	event, strain, time, chan_dic = loaddata_objects
	fs, NFFT, freqs, dt, strain_whiten = whiten_objects
	bb, ab, normalization, strain_whitenbp, template = plot_objects
	
	# Extra inputs
	deltat_sound = 2.
	tevent = event['tevent']
	indxd = np.where((time >= tevent-deltat_sound) & (time < tevent+deltat_sound))
	

	# write the files:
	wav_path = get_wav_path(file_code)
	ut.write_wavfile(wav_path, int(fs), strain_whitenbp[indxd])
	
	yield
	
	os.remove(wav_path)
