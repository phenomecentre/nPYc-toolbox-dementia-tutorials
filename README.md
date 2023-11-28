# nPYc-toolbox-dementia-tutorials

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/phenomecentre/nPYc-toolbox-dementia-tutorials/master)

The tutorials in this repository use Jupyter notebooks to demonstrate the application of the [nPYc-Toolbox](https://github.com/phenomecentre/nPYc-Toolbox) for the preprocessing and quality control of exemplar LC-MS and NMR metabolic profiling datasets. These tutorials work through each step in detail, with links to relevant documentation, hosted on [Read the Docs](http://npyc-toolbox.readthedocs.io/en/latest/index.html).

For full details on installation and the tutorial datasets see [Installation and Tutorials](https://npyc-toolbox.readthedocs.io/en/latest/tutorial.html), however, in brief, this repository provides:

 - Preprocessing_and_Quality_Control_of_Dementia_Cohort_LC-MS_Data_with_the_nPYc-Toolbox.ipynb: Jupyter notebook tutorial for LC-MS RPOS (XCMS) data
 - Preprocessing_and_Quality_Control_of_Dementia_Cohort_NMR_Data_with_the_nPYc-Toolbox.ipynb: Jupyter notebook tutorial for NMR (Bruker) data
 
Alongside all required exemplar datasets and associated files:

 - Dementia_Urine_LCMS_RPOS_XCMS.csv: feature extracted (XCMS) LC-MS RPOS data
 - ALZ_Urine_Rack01_RCM_221214: folder containing the 1D NMR raw data files
 - DDementia_Urine_LCMS_RPOS_basicCSV and Dementia_Urine_NMR_basicCSV.csv: CSV files containing basic sample associated information about each of the acquired samples for each dataset

The dataset used in this example is obtained from the metabolic phenotyping of human urine samples from the dementia cohort. In this sample set, baseline spot urine samples (first sample collected after recruitment to the study) were collected as part of the AddNeuroMed1 and ART/DCR study consortia, with the aim of identifying biomarkers of neurocognitive decline and Alzheimer’s disease. See [Original Paper](https://doi.org/10.1111/j.1749-6632.2009.05064.x).

The dataset is comprised of 708 samples of human urine, aliquoted, and independently prepared and measured by ultra-performance liquid chromatography coupled to reversed-phase positive ionisation mode spectrometry (LC-MS, RPOS). The same sample set was also acquired by nuclear magnetic resonance (NMR) spectroscopy, and here (owing to space limitiations) we include the first rack (comprising 80 samples) of NMR data. A pooled QC sample (study reference, SR) and independent external reference (long-term reference, LTR) of a comparable matrix was also acquired to assist in assessing analytical precision. See the Metabolights Study [MTBLS719](https://www.ebi.ac.uk/metabolights/MTBLS719) for details of the study, and [Recommended Study Design Elements](https://npyc-toolbox.readthedocs.io/en/latest/studydesign.html) for details of the various QC samples acquired.
