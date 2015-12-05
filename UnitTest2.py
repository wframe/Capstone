from utilz import *
if __name__ == '__main__':
    #songs = pload('songs.pkl')
    #ssongs = sorted(songs, key=lambda x: len(x.eventset), reverse=True)

    #song length outliers
    #print('top ten:' + "".join(['file ' + song.filename + ' had ' + str(len(song.eventset)) + ' events \n' for song in ssongs[:10]]))
    #print('last ten:' + "".join(list(reversed(['file ' + song.filename + ' had ' + str(len(song.eventset)) + ' events \n' for song in ssongs[-10:]]))))

    features = pload('featurevectors.pkl')
    
    #top features
    featurecounter = Counter([feature.vector for feature in features])
    #map(SemanticizeFeature,featurecounter.most_common(129))
    #print(sum([i[1] for i in featurecounter.most_common(128)]))
    print('total rests: ' +str(sum([1 if i[0]==1 else 0 for i in featurecounter.elements()])))
    print('unique rests: ' +str(len(list(set(([i for i in featurecounter.elements() if i[0]==1]))))))