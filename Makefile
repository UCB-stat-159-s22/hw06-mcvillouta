PNG_FILES = $(wildcard figures/*.png)
CSV_FILES = $(wildcard tables/*.csv)
WAV_FILES = $(wildcard audio/*.wav)

#Build Jupyter Book
html: 
	jupyter-book build .

conf.py: _config.yml _toc.yml
	jupyter-book config sphinx .

html-hub: conf.py
	sphinx-build  . _build/html -D html_baseurl=${JUPYTERHUB_SERVICE_PREFIX}/proxy/absolute/8000
	@echo "Start the Python http server and visit:"
	@echo "https://stat159.datahub.berkeley.edu/user-redirect/proxy/8000/index.html"

# Run Jupyter Notebook to obtain figures, audio files, and table
.PHONY : all
all :
	jupyter execute index.ipynb

# Clean figures, audio, table, and build book
.PHONY : clean
clean :
	rm -f $(PNG_FILES)
	rm -f $(CSV_FILES)
	rm -f $(WAV_FILES)
	rm -rf _build/html/

#Create Environment
.PHONY: env
env:
	mamba env create -f environment.yml -p ~/envs/ligo
	bash -ic 'conda activate ligo;python -m ipykernel install --user --name ligo --display-name "IPython - ligo"'

.PHONY : variables
variables :
	@echo PNG_FILES: $(PNG_FILES)
	@echo CSV_FILES: $(CSV_FILES)
	@echo CSV_FILES: $(WAV_FILES)

