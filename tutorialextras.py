import pandas
from datetime import datetime
import numpy
from nPYc.enumerations import VariableType, DatasetLevel, AssayRole, SampleType

def matchBasicCSV(dataset, filePath):
	"""
	Do a basic join of the data in the csv file at filePath to the :py:attr:`sampleMetadata` dataframe on the 'Sample File Name'.
	"""

	dateparse = lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M')

	csvData = pandas.read_csv(filePath, dtype={'Sample File Name':str, 'Sample ID': str}, parse_dates=['Acquired Time'], date_parser=dateparse)
	currentMetadata = dataset.sampleMetadata.copy()

	if 'Sample File Name' not in csvData.columns:
		raise KeyError("No 'Sample File Name' column present, unable to join tables.")

	# Check if there are any duplicates in the csv file
	u_ids, u_counts = numpy.unique(csvData['Sample File Name'], return_counts=True)
	if any(u_counts > 1):
		warnings.warn('Check and remove duplicates in CSV file')
		return

	# Store previous AssayRole and SampleType in case they were parsed using from filename:
	#
	oldAssayRole = currentMetadata['AssayRole']
	oldSampleType = currentMetadata['SampleType']
	oldDilution = currentMetadata['Dilution']
	##
	# If colums exist in both csv data and dataset.sampleMetadata remove them from sampleMetadata
	##
	columnsToRemove = csvData.columns
	columnsToRemove = columnsToRemove.drop(['Sample File Name'])

	for column in columnsToRemove:
		if column in currentMetadata.columns:
			currentMetadata.drop(column, axis=1, inplace=True)

	# If AssayRole or SampleType columns are present parse strings into enums

	csvData['AssayRole'] = [(x.replace(" ", "")).lower() if type(x) is str else numpy.nan for x in csvData['AssayRole']]
	csvData['SampleType'] = [(x.replace(" ", "")).lower() if type(x) is str else numpy.nan for x in csvData['SampleType']]

	if 'AssayRole' in csvData.columns:
		for role in AssayRole:
			csvData.loc[csvData['AssayRole'].values == (str(role).replace(" ",  "")).lower(), 'AssayRole'] = role
	if 'SampleType' in csvData.columns:
		for stype in SampleType:
			csvData.loc[csvData['SampleType'].values == (str(stype).replace(" ", "")).lower(), 'SampleType'] = stype

	# If Acquired Time column is in the CSV file, reformat data to allow operations on timestamps and timedeltas,
	# which are used in some plotting functions
	if 'Acquired Time' in csvData:
		csv_datetime = pandas.to_datetime(csvData['Acquired Time'], errors='ignore')
		# msData.sampleMetadata['Acquired Time'] = z
		csv_datetime = csv_datetime.dt.strftime('%d-%b-%Y %H:%M:%S')
		csvData['Acquired Time'] = csv_datetime.apply(lambda x: datetime.strptime(x, '%d-%b-%Y %H:%M:%S')).astype('O')

	# Left join, without sort, so the intensityData matrix and the sample Masks are kept in order
	# Preserve information about sample mask alongside merge even on the case of samples missing from CSV file.

	# Is this required?? Masked field doesn't seem to be used anywhere else
	currentMetadata['Masked'] = False
	currentMetadata.loc[(dataset.sampleMask == False), 'Masked'] = True

	joinedTable = pandas.merge(currentMetadata, csvData, how='left', left_on='Sample File Name',
							   right_on='Sample File Name', sort=False)

	merged_samples = pandas.merge(currentMetadata, csvData, how='inner', left_on='Sample File Name',
							   right_on='Sample File Name', sort=False)

	merged_samples = merged_samples['Sample File Name']

	merged_indices = joinedTable[joinedTable['Sample File Name'].isin(merged_samples)].index

	# Samples in the CSV file but not acquired will go for sampleAbsentMetadata, for consistency with NPC Lims import
	csv_butnotacq = csvData.loc[csvData['Sample File Name'].isin(currentMetadata['Sample File Name']) == False, :]

	if csv_butnotacq.shape[0] != 0:
		sampleAbsentMetadata = csv_butnotacq.copy(deep=True)
		# Removed normalised index columns
		# Enum masks describing the data in each row
		sampleAbsentMetadata.loc[:, 'SampleType'] = SampleType.StudySample
		sampleAbsentMetadata.loc[sampleAbsentMetadata['SampleType'].str.match('StudyPool', na=False).astype(
			bool), 'SampleType'] = SampleType.StudyPool
		sampleAbsentMetadata.loc[sampleAbsentMetadata['SampleType'].str.match('ExternalReference', na=False).astype(
			bool), 'SampleType'] = SampleType.ExternalReference

		sampleAbsentMetadata.loc[:, 'AssayRole'] = AssayRole.Assay
		sampleAbsentMetadata.loc[sampleAbsentMetadata['AssayRole'].str.match('PrecisionReference', na=False).astype(
			bool), 'AssayRole'] = AssayRole.PrecisionReference
		sampleAbsentMetadata.loc[sampleAbsentMetadata['AssayRole'].str.match('LinearityReference', na=False).astype(
			bool), 'AssayRole'] = AssayRole.LinearityReference

		# Remove duplicate columns (these will be appended with _x or _y)
		cols = [c for c in sampleAbsentMetadata.columns if c[-2:] != '_y']
		sampleAbsentMetadata = sampleAbsentMetadata[cols]
		sampleAbsentMetadata.rename(columns=lambda x: x.replace('_x', ''), inplace=True)

		dataset.sampleAbsentMetadata = sampleAbsentMetadata

	# By default everything in the CSV has metadata available and samples mentioned there will not be masked
	# unless Include Sample field was == False
	joinedTable.loc[merged_indices, 'Metadata Available'] = True

	# Samples in the folder and processed but not mentioned in the CSV.
	acquired_butnotcsv = currentMetadata.loc[(currentMetadata['Sample File Name'].isin(csvData['Sample File Name']) == False), :]

	# Ensure that acquired but no csv only counts samples which 1 are not in CSV and 2 - also have no other kind of
	# AssayRole information provided (from parsing filenames for example)
	if acquired_butnotcsv.shape[0] != 0:

		noMetadataIndex = acquired_butnotcsv.index
		# Find samples where metadata was there previously and is not on the new CSV
		previousMetadataAvailable = currentMetadata.loc[(~oldSampleType.isnull()) & (~oldAssayRole.isnull())
														& ((currentMetadata['Sample File Name'].isin(csvData['Sample File Name']) == False)), :].index
		metadataNotAvailable = [x for x in noMetadataIndex if x not in previousMetadataAvailable]
		# Keep old AssayRoles and SampleTypes for cases not mentioned in CSV for which this information was previously
		# available
		joinedTable.loc[previousMetadataAvailable, 'AssayRole'] = oldAssayRole[previousMetadataAvailable]
		joinedTable.loc[previousMetadataAvailable, 'SampleType'] = oldSampleType[previousMetadataAvailable]
		joinedTable.loc[previousMetadataAvailable, 'Dilution'] = oldDilution[previousMetadataAvailable]
		
		#  If not in the new CSV, but previously there, keep it and don't mask
		if len(metadataNotAvailable) > 0:
			joinedTable.loc[metadataNotAvailable, 'Metadata Available'] = False
#				dataset.sampleMask[metadataNotAvailable] = False
#				joinedTable.loc[metadataNotAvailable, 'Exclusion Details'] = 'No Metadata in CSV'

	# 1) ACQ and in "include Sample" - drop and set mask to false
	#  Samples Not ACQ and in "include Sample" set to False - drop and ignore from the dataframe

	# Remove acquired samples where Include sample column equals false - does not remove, just masks the sample
	if 'Include Sample' in csvData.columns:
		which_to_drop = joinedTable[joinedTable['Include Sample'] == False].index
		#dataset.intensityData = numpy.delete(dataset.intensityData, which_to_drop, axis=0)
		#dataset.sampleMask = numpy.delete(dataset.sampleMask, which_to_drop)
		dataset.sampleMask[which_to_drop] = False
		#joinedTable.drop(which_to_drop, axis=0, inplace=True)
		joinedTable.drop('Include Sample', inplace=True, axis=1)

	previously_masked = joinedTable[joinedTable['Masked'] == True].index
	dataset.sampleMask[previously_masked] = False
	joinedTable.drop('Masked', inplace=True, axis=1)
	# Regenerate the dataframe index for joined table
	joinedTable.reset_index(inplace=True, drop=True)
	dataset.sampleMetadata = joinedTable

	# Commented out as we shouldn't need this here after removing the LIMS, but lets keep it
	# This should make it work - but its assuming the sample "NAME" is the same as File name as in LIMS.
	dataset.sampleMetadata['Sample Base Name'] = dataset.sampleMetadata['Sample File Name']

	# Ensure there is a batch column
	if 'Batch' not in dataset.sampleMetadata:
		dataset.sampleMetadata['Batch'] = 1

	dataset.Attributes['Log'].append([datetime.now(), 'Basic CSV matched from %s' % (filePath)])

	return dataset