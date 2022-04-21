
import os
import pytest

VERBOSE = 1

@pytest.fixture(scope='session', autouse=True)
def repo_path():
	# If ran from ligotools folder
	#path = os.path.abspath(os.path.join('..'))
	# If ran from repo folder
	path = os.getcwd()
	return path

def join_repo_path(filename):
	print(repo_path)
	file_path = os.path.join(repo_path, filename)
	if VERBOSE:
		print(f"Current path: {os.getcwd()}")
		print(f"Repo path: {repo_path}")
		print(f"File path: {file_path}")
	return file_path

@pytest.fixture(scope='session', autouse=True)
def strain_time_chan(request):
	"""
		request.param in ['H1', 'L1']
	"""
	
	# Parameters
	eventname = 'GW150914'
	fnjson = join_repo_path("BBH_events_v3.json")
	events = json.load(open(fnjson,"r"))
	event = events[eventname]
	filename = event[f'fn_{request.param}']
	file_path = join_repo_path(filename)	
		
	# Load data
	strain, time, chan_dict = loaddata(file_path, file_code)
	
	return strain, time, chan_dict
