﻿from SongData import *
from utilz import *
def initializetrajectory(startstates):
    start = drawStart(startstates)
    startbeat = start.beat			
    startpitch = previousPitch = start.pitch
    startaction = start.actiongenerated    
    event = findevent(actiontaken=startaction,pitchmode=startpitch)	#second event, first after start state
    context = SongContextState(startpitch,startbeat)
    node = Node(context=context, feature=None, parent=start, prospects=None, action=None)
    print('Initialized trajectory--')
    start.display()
    node.display()
    return start, event, node

def recoverShrunkenFeatures(node, pca):		
    features = []	    
    while node is not None and type(node) is not StartState:
        parent = node.parent
        feature = pca.transform(node.feature.vector)
        features.append(feature)
        node = parent
    return list(reversed(features))


def RecursiveSearchForEnd(node,newevent):
    #print('beat: ' + str(node.context.currentBeatIndex+1) + ' new event: ' + str(newevent))
    context = copy.deepcopy(node.context)   
    context.update(newevent)
    node.context = context
    node.feature = context.feature.vector
    #printOnes(node.feature)
    if node.feature not in observedstates:
        prospects = sexuallyGenerateProspects(observedstates)
        node.canonicalprospects = prospects
        node.prospects = prospects
        node.isMutant = True
    else:
        node.prospects = copy.deepcopy(observedstates[node.feature])
    #print('Prospects: ' + str(node.prospects))
    while len(node.prospects.keys()) > 0:
        action = drawActionNoRep(node.prospects)
        del node.prospects[action]
        node.actiongenerated = action 
        if action == SongData.END:
            print('completed song')
            return node
        newevent = findevent(action, node.context.songPitchMap.getPitchMax(SongData.REST))

        lastscion = RecursiveSearchForEnd(Node(context, None, node, None, None), newevent)

        if lastscion is not None and lastscion.actiongenerated == SongData.END:	
            return lastscion
def updateNodeAndFeature(node,event,tfam,pca,cmodels):
        context = copy.deepcopy(node.context)   
        context.update(event)
        node.context = context
        if event == SongData.END:
            node.feature = SongData.END
        else:
            node.feature = context.feature
            node.transformFeatureAttributes(tfam, pca, cmodels)
def GenerateSongEvents(firstnode,firstevent,tfam,pca,cmodels):

    updateNodeAndFeature(firstnode,firstevent,tfam,pca,cmodels) 

    parent = firstnode
    eventnumber = 1
    while True:
        eventnumber+=1

        action = parent.actiongenerated = drawActionNoRep(parent.transformedprospects)  
        
        if action is SongData.END:
            print('events: ' + str(eventnumber))
            return parent
                     
        event = findevent(action, parent.context.songPitchMap.getPitchMax(SongData.REST))

        child =  Node(parent.context, None, parent, None, None)
        updateNodeAndFeature(child,event,tfam,pca,cmodels)
        parent = child
         
def Main(TOTALSONGSTOMONTECARLO = 250):

    startstates, features, tfam, pca, cmodels= getRawFeaturePickles(),getDerivedPickles()
    policy = dict()

    songs= []
    overflownstax = 0
    #arbitrary 0 vector for broadcast
    accumulations = [0]
    while len(songs) < TOTALSONGSTOMONTECARLO:
        print('total songs:' + str(len(songs)+1))
        start, event, node = initializetrajectory(startstates)
        try:
            terminal =GenerateSongEvents(node,event,tfam,pca,cmodels)
            #terminal = RecursiveSearchForEnd(node,event)
            if terminal is not None:
                songs.append((start,terminal))
                feats = recoverShrunkenFeatures(terminal, pca)
                accumulations += discount_and_accumulate_ordered_feature_list(feats)
        except RuntimeError:
            print('stack overflow')
            overflownstax += 1
    pdump(accumulations/TOTALSONGSTOMONTECARLO,pricedsums_pickle_string)   
    print("overflownstax: " + str(overflownstax))

    def convertTrajectoryToMidi(songEnds):
        def getnextnote(index,actions):	
            new_index = next((jdx for jdx, x in enumerate(actions[index:]) if x!= SongData.HOLD), None)
            if new_index is None:
                return None
            return index + new_index

        def appendNote(restDuration, pitch, noteDuration,track):
            restDuration, noteDuration = int(restDuration), int(noteDuration) 
            on = midi.NoteOnEvent(tick=restDuration, velocity=20, pitch=pitch)
            track.append(on)
            off = midi.NoteOffEvent(tick=noteDuration, pitch=pitch)
            track.append(off)
        def actionsToEvents(startpitch,actions):
            events = []
            heap = PitchMap()
            heap.upsertPitch(startpitch)
            events.append(startpitch)
            for action in actions:
                if action < 128:
                    newpitch = action+heap.getPitchMax(SongData.REST)
                    heap.upsertPitch(newpitch)
                    events.append(newpitch)
                else:
                    events.append(action)
            return events
        start =	songEnds[0]		#start node
        node = songEnds[1]		#terminal node
        parent = node.parent
        events = []
        nodes = []
        while type(node) is not StartState:
            parent = node.parent
            nodes.append(node)
            events.append(findevent(node.actiongenerated,node.context.songPitchMap.getPitchMax(SongData.REST))) 
            if node.isMutant:
                if node.feature not in observedstates:
                    observedstates[node.feature] = Counter()
                observedstates[node.feature][node.actiongenerated]  += 1
            node = parent
        events.append(findevent(start.actiongenerated,start.pitch))
        events.append(start.pitch)
        events = events[::-1]
        valid = True
        for event in events:
            if event>131 or event<0:
                valid = False
        if not valid:
            return None
        print('events: ' + str(events))
        pattern = midi.Pattern()
        track = midi.Track()
        pattern.append(track)
        eventlength = 4*midi.Pattern().resolution/float(SongData.BEATS_PER_BAR)
        initialRestDuration = start.beat*eventlength
        idx = getnextnote(1,events)
        noteDuration = (idx) * eventlength
        appendNote(initialRestDuration,start.pitch,noteDuration,track)
        while idx != None and events[idx] != SongData.END:
            restDuration = 0
            if events[idx] == SongData.REST:
                current = idx
                idx = getnextnote(idx+1,events)			
                restDuration = idx - current 
            pitch = 0
            try:
                pitch = events[idx]
            except:
                print('ended on rest??')
                return None
            current = idx
            idx = getnextnote(idx+1,events)
            if idx is not None:
                noteDuration = (idx - current) * eventlength	
                appendNote(restDuration, pitch, noteDuration,track)
        track.append(midi.EndOfTrackEvent(tick=1))
        midi.write_midifile(os.path.join('walks',str(uuid.uuid4())+'.mid'),pattern)	
    
    for idx,songEnds in enumerate(songs):
        convertTrajectoryToMidi(songEnds)
    
if __name__ == '__main__':
    featurevectors, startstates = getRawFeaturePickles()
 
    tfam, pca, cmodels = getDerivedPickles()
    Main()



            
            

    
        
        

                
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        