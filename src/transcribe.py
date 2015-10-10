import project_setup
import operator
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
        return "NOTE, note: " + str(self.note) + ", time: " + str(self.time) + ", length: " + str(self.length) + "\n"

def notesToMidi(notes):
    print "printing MIDI"
    pattern = midi.Pattern()
    # Instantiate a MIDI Track (contains a list of MIDI events)
    track = midi.Track()
    # Append the track to the pattern
    pattern.append(track)
    # Instantiate a MIDI note on event, append it to the track
    on = midi.NoteOnEvent(tick=0, velocity=100, pitch=midi.G_3)
    track.append(on)
    # Instantiate a MIDI note off event, append it to the track
    off = midi.NoteOffEvent(tick=100000, pitch=midi.G_3)
    track.append(off)
    # Add the end of track event, append it to the track
    eot = midi.EndOfTrackEvent(tick=1)
    track.append(eot)
    # Print out the pattern
    print pattern
    # Save the pattern to disk
    midi.write_midifile("example.mid", pattern) 

def extract_tracks():
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
    print midi_files
    for filepath in midi_files:
        filename = os.path.splitext(os.path.basename(filepath))[0]
        pattern =  midi.read_midifile(filepath)

        print filename
        if (filename != "sm3warp"):
            pass
            #continue

        # Write pattern to file
        fo = open(trans_dir + '/' + filename + '.txt', "w")
        fo.write(str(pattern))
        fo.close()
        
        for index, track in enumerate(pattern):
            notes = []
            seenNotes = {}
            trackname = None

            for event in sorted(track, key=lambda x: x.tick, reverse=False):
                print "event time: " + str(event.tick)

                # Get track name if it exists
                if isinstance(event, midi.TrackNameEvent):
                    trackname = event.text
                    
                # ensure we're dealing with a note change event
                if ((not isinstance(event, midi.NoteOnEvent)) and (not isinstance(event, midi.NoteOffEvent))):
                    continue
                
                notePitch = event.data[0]
                noteTime = event.tick
                if isinstance(event, midi.NoteOnEvent):
                    print "adding note: " + str(event)
                    seenNotes[notePitch] = event
                elif isinstance(event, midi.NoteOffEvent):
                    if (notePitch not in seenNotes or seenNotes[notePitch] is None):
                        print "Error, found Off event with no corresponding On event."
                        continue
                    print "adding note for good: " + str(event)
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

    return tracks

def transitionTally (transitionDict, state1, state2):
    if state1 not in transitionDict:
        transitionDict[state1] = {}
    if state2 not in transitionDict[state1]:
        transitionDict[state1][state2] = 0
    transitionDict[state1][state2] = transitionDict[state1][state2] + 1

def extract_transitions(tracks):
    noteTransitions = {}
    lengthTransitions = {}
    restTransitions = {}
    # Process transition events from tracks
    for track in tracks.values():
        for index, note1 in enumerate(sorted(track)):
        #for index, note1 in enumerate(sorted(track, key=operator.attrgetter('time'), reverse=False)):
            # Find note2
            note2Found = False
            for candidateNote2 in sorted(track)[index:]:
                print "looking for note2"
            #for candidateNote2 in sorted(track, key=lambda x: x.time, reverse=False)[index:]:
                if (candidateNote2.time > note1.time and note2Found is False):
                    note2Found = True
                    note2 = candidateNote2
                    print ("note 1 time: " + str(note1.time) + ", note 2 time: " + str(note2.time))

                    # record note transition
                    transitionTally(noteTransitions, note1.note, note2.note)
                    transitionTally(lengthTransitions, note1.length, note2.length)
                    transitionTally(restTransitions, note1.note, note2.time - note1.time) # Note: this transition is using the note as the key
                    print "done transitions"

        print transitionTally
            
def main():
    """
    print "Extracting tracks..."
    tracks = extract_tracks()
    print tracks
    print "Extracting transitions..."
    transitions = extract_transitions(tracks)
    print "DONE"
    """
    notesToMidi(None)



if __name__ == "__main__":
    main()

