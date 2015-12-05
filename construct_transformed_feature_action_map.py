from utilz import *
def Main():
    from SongData import FeatureVector    
    pca, cmodels = getModelPickles()
    tfam = dict()
    tfam[0] = dict()
    tfam[1] = dict()

    features = pload(featurevector_pickle_string)
    vectorset = set([f.vector for f in features])
    print('mapping features to clusters... current time is: ' + str(datetime.datetime.now().time()))
    featureclustermap =  dict((vector,DimReducer(vector,[pca.transform,clustermodelheuristic(vector,cmodels).predict])[0]) for vector in list(vectorset))

    pdump(featureclustermap, fcm_pickle_string)

    for idx,feature in enumerate(features):
        if idx%1000==0:
            print('adding the ' + str(idx/1000) + ' thousandth transformed feature.. current time is: ' + str(datetime.datetime.now().time()))
        original = feature.vector
        tfeat= featureclustermap[original]
        parity = original[0]
        if tfeat not in tfam[parity]:
            tfam[parity][tfeat] = Counter()
        featureactions = tfam[parity][tfeat]
        featureactions[feature.actiongenerated] += 1
    pdump(tfam, tfam_pickle_string)
if __name__ == '__main__':
    Main()