import project_setup
import midi
import os
import glob

midi_dir = project_setup.PROJECT_HOME + '/data/midi'
trans_dir = project_setup.PROJECT_HOME + '/data/transcriptions'
notes_dir = project_setup.PROJECT_HOME + '/data/notes'
tracks = {}

class Note:
    def __init__(self, note, time, length):
        self.note = note
        self.time = time
        self.length = length
    
    def __repr__(self):
        return "NOTE, note: " + str(self.note) + ", time: " + str(self.time) + ", length: " + str(self.length)

#/ Create directory if it doesn't exist
if not os.path.exists(trans_dir):
    os.makedirs(trans_dir)
if not os.path.exists(notes_dir):
    os.makedirs(notes_dir)

# Clean out existing transcriptions
files_to_delete = glob.glob(trans_dir + '/*')
for f in files_to_delete :
    os.remove(f)

# Get list of midi files and transcribe them
midi_files = glob.glob(midi_dir + "/*.mid")
for filepath in midi_files:
    filename = os.path.splitext(os.path.basename(filepath))[0]
    pattern =  midi.read_midifile(filepath)

    # Write pattern to file
    fo = open(trans_dir + '/' + filename + '.txt', "w")
    fo.write(str(pattern))
    fo.close()
    
    for index, track in enumerate(pattern):
        notes = []
        seenNotes = {}
        trackname = None

        for event in sorted(track):

            # Get track name if it exists
            if isinstance(event, midi.TrackNameEvent):
                trackname = event.text
                print trackname
                
            # ensure we're dealing with a note change event
            if ((not isinstance(event, midi.NoteOnEvent)) and (not isinstance(event, midi.NoteOffEvent))):
                continue
            
            notePitch = event.data[0]
            noteTime = event.tick
            if isinstance(event, midi.NoteOnEvent):
                seenNotes[notePitch] = event
            elif isinstance(event, midi.NoteOffEvent):
                if (notePitch not in seenNotes or seenNotes[notePitch] is None):
                    print "Error, found Off event with no corresponding On event."
                    continue
                notes.append(Note(notePitch, seenNotes[notePitch].tick, noteTime - seenNotes[notePitch].tick))

        # Save this track's notes if it has notes
        if len(notes)>1:

            if trackname is not None:
                notesFilename = filename + "_" + str(index) + "_" + trackname
            else:
                notesFilename = filename + "_" + str(index)
            tracks[notesFilename] = notes
                
            # Write track's notes to file
            fo = open(notes_dir + '/' + notesFilename + '.txt', "w")
            fo.write(str(notes))
            fo.close()





