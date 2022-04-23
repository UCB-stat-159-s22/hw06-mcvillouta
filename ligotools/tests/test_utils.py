
import os
import json
import pytest
import numpy as np

from ligotools import readligo as rl
from ligotools import utils as ut
from ligotools.tests import conftest as cf


@pytest.mark.parametrize('file_code', ['H1', 'L1'])
def test_whiten(get_various_ligotools_objects, file_code):
	
	# Various ligotools objects
	loaddata_objects, whiten_objects, plot_objects = get_various_ligotools_objects(file_code)
	fs, NFFT, freqs, dt, strain_whiten = whiten_objects
	
	assert isinstance(strain_whiten, np.ndarray) and len(strain_whiten)>0
	assert isinstance(freqs, np.ndarray) and len(freqs)>0
	assert isinstance(dt, np.float64) and dt>0


@pytest.mark.parametrize('file_code', ['H1', 'L1'])
def test_make_figures(build_figures, file_code):
	
	fn_plot1, fn_plot2, fn_plot3 = cf.get_figures_path(file_code)

	assert os.path.isfile(fn_plot1)
	assert os.path.isfile(fn_plot1)
	assert os.path.isfile(fn_plot1)


@pytest.mark.parametrize('file_code', ['H1', 'L1'])
def test_write_wavfile(build_wavfile, file_code):
	
	wav_path = cf.get_wav_path(file_code)
	
	assert os.path.isfile(wav_path)


@pytest.mark.parametrize('file_code', ['H1', 'L1'])
def test_reqshift(get_various_ligotools_objects, file_code):
	
	# Various ligotools objects
	loaddata_objects, whiten_objects, plot_objects = get_various_ligotools_objects(file_code)
	bb, ab, normalization, strain_whitenbp, template = plot_objects	
	
	strain_shifted = ut.reqshift(strain_whitenbp)
	
	assert isinstance(strain_shifted, np.ndarray) and len(strain_shifted) > 0
	
	