import os
#root = os.path.join('C:\\', 'Users', 'William','Documents','GitHub','Capstone')
root = os.path.join('C:\\', 'Users','William','Desktop','CapstoneFiles','Capstone')

pickleDir=os.path.join('C:\\', 'Users','William','Desktop','CapstoneFiles','Pickles')
datasetDir=os.path.join('scripts','scripts','melodies','noChords')

outputmodelname = 'ADDEDHOLDFEAT'
inputmodelname = outputmodelname

pca_pickle_string = 'pca.pkl'
ncluster_pickle_string = 'NFeatureCLustr.pkl'
rcluster_pickle_string = 'RFeatureCLustr.pkl'
songs_pickle_string = 'songs.pkl'
featurevector_pickle_string = 'featurevectors.pkl'
startstate_pickle_string = 'startstates.pkl'
tfam_pickle_string = 'tfam.pkl'
fcm_pickle_string = 'fcm.pkl'
pricedsums_pickle_string = 'pricedsums.pkl'
valid_filename_pickle_string = "valid_filenames.pkl"

PCA_components = .95