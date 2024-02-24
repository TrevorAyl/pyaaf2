import sys
import aaf2
import json
import math
from datetime import datetime

## NB - this is called by the tally-timer index.js with argument (events)
## NOW has master mobs = sequence length created and used 
## TODO - increase number of arguments from index.js so nothing needs to be changed in here
## TODO - add V2 with PGM add-edits
## TODO - think about audio

def _seconds(value):
    if isinstance(value, str):  # value seems to be a timestamp
        _zip_ft = zip((3600, 60, 1, 1/frame_rate), value.split(':'))
        result = sum(f * float(t) for f,t in _zip_ft) 
        return result 
    elif isinstance(value, (int, float)):  # frames
        return value / framerate
    else:
        return 0

def _timecode(seconds):
    return '{h:02d}:{m:02d}:{s:02d}:{f:02d}' \
            .format(h=int(seconds/3600),
                    m=int(seconds/60%60),
                    s=int(seconds%60),
                    f=round((seconds-int(seconds))*frame_rate))

def _frames(seconds):
    return seconds * frame_rate

def timecode_to_frames(timecode, start=None):
    return _frames(_seconds(timecode) - _seconds(start))

def msToFrames(ms):
    return round(ms/1000*frame_rate)

def msToHMS(ms):
    seconds=int(ms/1000)%60
    minutes=int(ms/(1000*60))%60
    hours=int(ms/(1000*60*60))%24
    return str(hours).zfill(2) + "_" + str(minutes).zfill(2) + "_" + str(seconds).zfill(2)

def frames_to_TC(total_frames, frame_rate, drop=False):
    if drop and frame_rate not in [29.97, 59.94]:
        raise NotImplementedError("Time code calculation logic only supports drop frame "
                                  "calculations for 29.97 and 59.94 fps.")
    fps_int = int(round(frame_rate))

    if drop:
        FRAMES_IN_ONE_MINUTE = 1800 - 2
        FRAMES_IN_TEN_MINUTES = (FRAMES_IN_ONE_MINUTE * 10) - 2
        ten_minute_chunks = total_frames / FRAMES_IN_TEN_MINUTES
        one_minute_chunks = total_frames % FRAMES_IN_TEN_MINUTES
        ten_minute_part = 18 * ten_minute_chunks
        one_minute_part = 2 * ((one_minute_chunks - 2) / FRAMES_IN_ONE_MINUTE)
        if one_minute_part < 0:
            one_minute_part = 0
        # add extra frames
        total_frames += ten_minute_part + one_minute_part

        # for 60 fps drop frame calculations, we add twice the number of frames
        if fps_int == 60:
            total_frames = total_frames * 2

        # time codes are on the form 12:12:12;12
        smpte_token = ";"

    else:
        # time codes are on the form 12:12:12:12
        smpte_token = ":"

    # now split our frames into time code
    hours = int(total_frames / (3600 * fps_int))
    minutes = int(total_frames / (60 * fps_int) % 60)
    seconds = int(total_frames / fps_int % 60)
    frames = int(total_frames % fps_int)
    return "%02d:%02d:%02d%s%02d" % (hours, minutes, seconds, smpte_token, frames)
 
# get current date and time
current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
 
# convert datetime obj to string
str_current_datetime = str(current_datetime)


if len(sys.argv) > 1:
    # Data from tally-timer when this script is called from index.js
    events = json.loads(sys.argv[1]) 
    dictClipColors = json.loads(sys.argv[2])
    pgmTapeName = json.loads(sys.argv[3])
    sequence_name = 'TallyLog ' + msToHMS(events["start"]) + ' - ' +msToHMS(events["end"])
    file_name = "/Users/trevoraylward/Documents/GitHub/_TallyToAAF/data/" + sequence_name + '.aaf'
else:
    # FOR TESTING - sample data
    events = {'start': 63764379, 'end': 63770094, 'clips': [{'TIME': 63764829, 'TEXT': 'C-05'}, {'TIME': 63765643, 'TEXT': 'C-06'}, {'TIME': 63766455, 'TEXT': 'C-07'}, {'TIME': 63767268, 'TEXT': 'C-08'}, {'TIME': 63768078, 'TEXT': 'C-09'}, {'TIME': 63768893, 'TEXT': 'C-10'}]}
    dictClipColors = {'C-05': [120, 28, 129], 'C-06': [64, 67, 153], 'C-07': [72, 139, 194], 'C-08': [107, 178, 140], 'C-09': [159, 190, 87], 'C-10': [210, 179, 63]}
    pgmTapeName = "enterPGMtapeNameHere"
    sequence_name = 'TestTallyLog ' + msToHMS(events["start"]) + ' - ' +msToHMS(events["end"])
    file_name = "/Users/trevoraylward/Documents/GitHub/_TallyToAAF/data/" + sequence_name + '.aaf'

# Add PGM
dictClipColors['PGM']=[80,100,80]


# g=open("test_events.txt", "w")
# g.write(str(events))
# g.close

# g=open("test_dictClipColors.txt", "w")
# g.write(str(dictClipColors))
# g.close

# g=open("test_pgmTapeNames.txt", "w")
# g.write(str(pgmTapeName))
# g.close


comments = True

frame_rate = 50
frame_rate = frame_rate
frames = 0
tc = ""

# Container for MasterMobs
dictMobID = {}

# Getting sequence start from first event
clip_start = events["clips"][0]['TIME']
clip_start = msToFrames(clip_start)
sequence_start = clip_start


# The end makes sense as there is not necessarily an 'event' 
frames = msToFrames(events["end"])
tc = frames_to_TC (frames,frame_rate, False)
sequence_end = frames

sequence_length = sequence_end - sequence_start

with aaf2.open(file_name, "w")  as f:
    # Composition Mob created first
    comp_mob = f.create.CompositionMob()
    comp_mob.name = sequence_name
    # TODO - make this a function that makes sends
    # Adds color to sequence
    comp_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_R", 12000))
    comp_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_G", 16000))
    comp_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_B", 60000))

   # Create a TimelineMobSlot with a Timecode Segment for the start timecode
    tc_segment = f.create.Timecode(frame_rate)
    tc_segment.start = sequence_start
    tc_slot = comp_mob.create_timeline_slot(edit_rate=frame_rate, slot_id=1)
    tc_slot.segment = tc_segment

    # Sequence contains ??
    sequence = f.create.Sequence(media_kind="picture", length = sequence_length)
    
    # # Timeline slot contains the pictures?
    # timeline_slot = comp_mob.create_timeline_slot(frame_rate, slot_id=2)
    # timeline_slot.segment = sequence
    
    timecode_fps = frame_rate
    test_path = "some_path.mov"


    for key in dictClipColors.keys():

        # tape_name = event['TEXT'] # Tape name from source
        tape_name = key
        # tape_name = pgmTapeName # Tape name from PGM

        if tape_name == "":
            tape_name="unknown"

        # Make the Tape MOB
        tape_mob = f.create.SourceMob()
        
        tape_slot, tape_timecode_slot = tape_mob.create_tape_slots(tape_name, frame_rate, timecode_fps)        
        
        # set start time for clip
        tape_timecode_slot.segment.start = clip_start
        #Reduces from default 12 hours
        tape_slot.segment.length = sequence_length

        f.content.mobs.append(tape_mob)

        # Make a FileMob
        file_mob = f.create.SourceMob()

        # Make a locator - not sure we need this
        loc = f.create.NetworkLocator()
        loc['URLString'].value = test_path # TODO - not sure hwat we need here

        file_description = f.create.CDCIDescriptor()
        file_description.locator.append(loc)

        file_description['ComponentWidth'].value = 8
        file_description['HorizontalSubsampling'].value = 4
        file_description['ImageAspectRatio'].value = '16/9'
        file_description['StoredWidth'].value = 1920
        file_description['StoredHeight'].value = 1080
        file_description['FrameLayout'].value = 'FullFrame'
        file_description['VideoLineMap'].value = [42, 0]
        file_description['SampleRate'].value = frame_rate
        file_description['Length'].value = 10

        file_mob.descriptor = file_description
        # This length affects length of master mob and in timeline
        tape_clip = tape_mob.create_source_clip(slot_id=1, length=sequence_length)
        slot = file_mob.create_picture_slot(frame_rate)
        slot.segment.components.append(tape_clip)

        f.content.mobs.append(file_mob)

        # Make the Master MOBs

        master_mob = f.create.MasterMob()
        master_mob.name = key
        clip_color = dictClipColors[key]

        if clip_color != "":
            master_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_R", clip_color[0]*256))
            master_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_G", clip_color[1]*256))
            master_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_B", clip_color[2]*256))        

        clip = file_mob.create_source_clip(slot_id=1)


        slot = master_mob.create_picture_slot(frame_rate)
        slot.segment.components.append(clip)

        # dictMobID[key] = master_mob.mob_id
        dictMobID[key] = master_mob
        f.content.mobs.append(master_mob)


    if comments:
        ems = f.create.EventMobSlot()
        ems['EditRate'].value = frame_rate
        ems['SlotID'].value = 1000
        # # doesn't work in avid unless you specify
        # # the same PhysicalTrackNumber as the target TimelineMobSlot.
        ems['PhysicalTrackNumber'].value = 1

        marker_sequence = f.create.Sequence("DescriptiveMetadata")
        marker = f.create.DescriptiveMarker()
        marker['Position'].value = 1
        marker['Comment'].value = "This is a comment"
        marker['CommentMarkerUser'].value = "easyLog"

        marker_sequence.components.append(marker)
        ems.segment = marker_sequence
        comp_mob.slots.append(ems)

    # Finally append everthing to content
    f.content.mobs.append(comp_mob)


    # Nested slots are multiple video tracks in the sequence
    for i in range(1,3):
        nested_slot = comp_mob.create_timeline_slot(frame_rate)
        nested_slot['PhysicalTrackNumber'].value = i
        # nested_slot.name = 'Slot_V_' + str(i)
        nested_scope = f.create.NestedScope()
        nested_slot.segment= nested_scope

        sequence = f.create.Sequence(media_kind="picture")
        nested_scope.slots.append(sequence)

        if i == 1 :
            nested_slot.name = 'SRC'
            clip_position = 0
            for i, event in enumerate(events["clips"]):

                clip_start = event['TIME']
                clip_start = msToFrames(clip_start)

                if i < len(events["clips"]) -1:
                    clip_end = events["clips"][i+1]['TIME']
                    clip_end = msToFrames(clip_end)
                else:
                    clip_end = sequence_end
                clip_length = clip_end - clip_start

                mm = (dictMobID[event['TEXT']])

                # Create a SourceClip
                clip = mm.create_source_clip(slot_id=1)
                # This is the start point of the master mob in the source clip?
                clip.start = clip_position
                # This is the length of the source clip - filled with the master mob
                clip.length = clip_length
                # this is that clip appended to the sequence
                sequence.components.append(clip)

                clip_position += clip_length

        if i == 2 :
            nested_slot.name = 'PGM'
            clip_position = 0
            for i, event in enumerate(events["clips"]):

                clip_start = event['TIME']
                clip_start = msToFrames(clip_start)

                if i < len(events["clips"]) -1:
                    clip_end = events["clips"][i+1]['TIME']
                    clip_end = msToFrames(clip_end)
                else:
                    clip_end = sequence_end
                clip_length = clip_end - clip_start

                mm = (dictMobID['PGM'])

                # Create a SourceClip
                clip = mm.create_source_clip(slot_id=1)
                # This is the start point of the master mob in the source clip?
                clip.start = clip_position
                # This is the length of the source clip - filled with the master mob
                clip.length = clip_length
                # this is that clip appended to the sequence
                sequence.components.append(clip)

                clip_position += clip_length


    # TODO Multiple audio tracks in the sequence
    for i in range(1,3):
        nested_slot = comp_mob.create_timeline_slot(frame_rate)
        nested_slot['PhysicalTrackNumber'].value = i
        nested_slot.name = 'Slot_A_' + str(i)
        nested_scope = f.create.NestedScope()
        nested_slot.segment= nested_scope

        sequence = f.create.Sequence(media_kind="sound")
        nested_scope.slots.append(sequence)
        comp_fill = f.create.Filler("sound", sequence_length)
        sequence.components.append(comp_fill)



