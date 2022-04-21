PNG_FILES = $(wildcard figures/*.png)
CSV_FILES = $(wildcard tables/*.csv)
WAV_FILES = $(wildcard tables/*.wav)

# Run Jupyter Notebook to obtain figures, audio files, and table
.PHONY : all
all :
	jupyter execute index.ipynb

# Clean figures, audio, and table
.PHONY : clean
clean :
	rm -f $(PNG_FILES)
	rm -f $(CSV_FILES)
	rm -f $(WAV_FILES)

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

