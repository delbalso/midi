import project_setup
import operator
import midi
import os
import glob
from modeling import MarkovChain

midi_dir = project_setup.PROJECT_HOME + '/data/midi'
trans_dir = project_setup.PROJECT_HOME + '/data/transcriptions'
notes_dir = project_setup.PROJECT_HOME + '/data/notes'
tracks_dir = project_setup.PROJECT_HOME + '/data/tracks'
output_midi_dir = project_setup.PROJECT_HOME + '/data/output_midi'
tracks = {}

class Note(object):
    def __init__(self, note, time, length):
        self.note = note
        self.time = time
        self.length = length

    def __eq__(self, otherNote):
           return self.note == otherNote.note and self.time == otherNote.time and self.length == otherNote.length

    def __hash__(self):
        return hash((self.note, self.time, self.length))

    def __repr__(self):

        return str((self.note, self.time, self.length))

def trackToNotelist(track):
    notes = []
    seenNotes = {}
    trackname = None

    for event in track:
        # ensure we're dealing with a note change event
        if ((not isinstance(event, midi.NoteOnEvent)) and (not isinstance(event, midi.NoteOffEvent))):
            continue
        #print str(event)
        notePitch = event.data[0]
        noteTime = event.tick
        #print "noteTime: "+str(noteTime)
        if isinstance(event, midi.NoteOnEvent):
            seenNotes[notePitch] = event
        elif isinstance(event, midi.NoteOffEvent):
            if (notePitch not in seenNotes or seenNotes[notePitch] is None):
                print "Error, found Off event with no corresponding On event."
                continue
            #print "Adding note: " + str(event)
            notes.append(Note(notePitch, seenNotes[notePitch].tick, noteTime))
            #print notes
            seenNotes[notePitch] = None
    return notes

def noteListToPattern(noteList):
    pattern = midi.Pattern(resolution=480)
    track = midi.Track()
    pattern.append(track)
    for note in noteList:
        on = midi.NoteOnEvent(tick=note.time, velocity=100, pitch=note.note)
        track.append(on)
        off = midi.NoteOffEvent(tick=note.length, pitch=note.note)
        track.append(off)
    track.append(midi.EndOfTrackEvent(tick=1))
    return pattern

# Write a NoteList to file
def writeNoteListToFile (notes, filename):
    fo = open(notes_dir + '/' + filename + '.txt', "w")
    fo.write(str(notes))
    fo.close()

def writeOutputPattern(pattern, filename):
    if not os.path.exists(output_midi_dir):
        os.makedirs(output_midi_dir)
    midi.write_midifile(output_midi_dir + "/" + filename + ".mid", pattern) 

def writeDebugTrack(track, filename, index):
    if not os.path.exists(tracks_dir):
        os.makedirs(tracks_dir)
    pattern = midi.Pattern()
    pattern.append(track)
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    #print "Writing debug track for "+filename+". Track #"+str(index)
    #print pattern
    midi.write_midifile(tracks_dir + "/" + filename + "_track"+str(index), pattern) 

def createExampleMidi(notes):
    print "printing MIDI"
    pattern = midi.Pattern()
    track = midi.Track()
    pattern.append(track)
    on = midi.NoteOnEvent(tick=0, velocity=100, pitch=midi.G_3)
    track.append(on)
    off = midi.NoteOffEvent(tick=100000, pitch=midi.G_3)
    track.append(off)
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    print pattern
    midi.write_midifile("example.mid", pattern) 

def getFileListToExtract(GivenTrack=None):
    # Create directory if it doesn't exist
    if not os.path.exists(trans_dir):
        os.makedirs(trans_dir)
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)

    # Clean out existing transcriptions
    files_to_delete = glob.glob(trans_dir + '/*')
    for f in files_to_delete :
        os.remove(f)

    # Get list of midi files and transcribe them
    if (GivenTrack == None):
        midi_files = glob.glob(midi_dir + "/*.mid")
    else: 
        midi_files = [midi_dir + "/" + GivenTrack + ".mid"]
    print "Files to extract: " + str(midi_files)
    return midi_files

def extractNoteListsFromFile(GivenTrack=None):
    midi_files = getFileListToExtract(GivenTrack)
    noteLists = []
    for filepath in midi_files:
        filename = os.path.splitext(os.path.basename(filepath))[0]
        print "Extracting: " + filename
        pattern =  midi.read_midifile(filepath)

        # Write pattern to file
        fo = open(trans_dir + '/' + filename + '.txt', "w")
        fo.write(str(pattern))
        fo.close()
        
        for index, track in enumerate(pattern):
            print "Processing track #" + str(index)
            writeDebugTrack(track, filename, index)
            noteList = trackToNotelist(track)
            # Save this track's notes if it has notes
            if len(noteList) > 1:
                writeNoteListToFile(noteList, filename+"_"+ str(index))
            noteLists.append(noteList)
    return noteLists
            
def main():
    print "Extracting tracks..."
    notelists = extractNoteListsFromFile("sm3warp")
    model = MarkovChain()
    model.trainFromNotelists(notelists, 1)
    sequence = model.generateSequence()
    pattern = noteListToPattern(sequence)
    writeOutputPattern(pattern, "test")
    print str(sequence)
    """
    createExampleMidi(None)
    """

if __name__ == "__main__":
    main()

