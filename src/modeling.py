import random

class MarkovChain(dict):
    def trainFromNotelists(self, noteLists, depth):
        assert len(noteLists)>0
        for noteList in noteLists:
            for i in range(len(noteList)):
                if i+depth+1 >= len(noteList):
                    break
                key_elements = []
                for j in range(depth):
                    key_elements.append(noteList[i+j])
                key = tuple (key_elements)
                value = noteList[i+j+1]
                #print "Adding to MC key: "+str(key)+" value: "+str(value)
                #print str(self)
                if key in self and isinstance(self[key], list):
                    self[key].append(value)
                else:
                    self[key] = [value]


    def generateSequence(self, seed=None, length=100):
        if seed == None: 
            seed = random.choice(self.keys())
        key_elements = list (seed)
        noteList = []
        for i in range(length):
            sampledNote = self.sample(tuple(key_elements))
            noteList.append(sampledNote)
            key_elements = key_elements[1:] 
            key_elements.append(sampledNote)
        return noteList

    def sample(self, key):
        assert key in self
        return random.choice(self[key])
