PNG_FILES = $(wildcard figures/*.png)
CSV_FILES = $(wildcard tables/*.csv)
WAV_FILES = $(wildcard audio/*.wav)

#Build Jupyter Book
.PHONY : html
html: 
	jupyter-book build .
	
.PHONY : html-hub
html-hub: 
	sphinx-build  . _build/html -D html_baseurl=${JUPYTERHUB_SERVICE_PREFIX}/proxy/absolute/8000
	@echo "To see Ligo Book visit: https://stat159.datahub.berkeley.edu/user-redirect/proxy/8000/index.html"
	cd _build/html && python -m http.server
	

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
	bash -ic 'conda activate ligo
	python -m ipykernel install --user --name ligo --display-name "IPython - ligo"'

.PHONY : variables
variables :
	@echo PNG_FILES: $(PNG_FILES)
	@echo CSV_FILES: $(CSV_FILES)
	@echo CSV_FILES: $(WAV_FILES)

