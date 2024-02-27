import sys
import aaf2
import json
import os
import logging
import math
from datetime import datetime


## NB - this is called by the tally-timer index.js with argument (events)
## NOW has master mobs = sequence length created and used 
## TODO - increase number of arguments from index.js so nothing needs to be changed in here
## TODO - think about audio

comments = True
frame_rate = 50
frames = 0
tc = ""

def _seconds(value):
    if isinstance(value, str):  # value seems to be a timestamp
        _zip_ft = zip((3600, 60, 1, 1/frame_rate), value.split(':'))
        result = sum(f * float(t) for f,t in _zip_ft) 
        return result 
    elif isinstance(value, (int, float)):  # frames
        return value / frame_rate
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

def convert_8_16bit(num):
    num /= 255
    num *= 65535
    return (int(num))


# get current date and time
current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
 
# convert datetime obj to string
str_current_datetime = str(current_datetime)


if len(sys.argv) > 1:
    # Data from tally-timer when this script is called from index.js
    events = json.loads(sys.argv[1]) 
    dictMasterMobInfo = json.loads(sys.argv[2])
    result_dir = json.loads(sys.argv[3]) 
    # result_dir = "/Users/trevoraylward/Documents/GitHub/_TallyToAAF/data/"

    sequence_name = 'TallyLog ' + msToHMS(events["start"]) + ' - ' +msToHMS(events["end"])
    file_name = result_dir + sequence_name + '.aaf'
else:
    # FOR TESTING - sample data
    events = {'start': 51213498, 'end': 51288501, 'clips': [{'TIME': 51213902, 'TEXT': 'C-05'}, {'TIME': 51214656, 'TEXT': 'C-06'}, {'TIME': 51215424, 'TEXT': 'C-07'}, {'TIME': 51216199, 'TEXT': 'C-08'}, {'TIME': 51216947, 'TEXT': 'C-09'}, {'TIME': 51217714, 'TEXT': 'C-10'}, {'TIME': 51218483, 'TEXT': 'C-01'}, {'TIME': 51219240, 'TEXT': 'C-02'}, {'TIME': 51219999, 'TEXT': 'i-25'}, {'TIME': 51220771, 'TEXT': 'i-30'}, {'TIME': 51221531, 'TEXT': 'C-05'}, {'TIME': 51222298, 'TEXT': 'C-06'}, {'TIME': 51223054, 'TEXT': 'C-07'}, {'TIME': 51223822, 'TEXT': 'C-08'}, {'TIME': 51224570, 'TEXT': 'C-09'}, {'TIME': 51225334, 'TEXT': 'C-10'}, {'TIME': 51226096, 'TEXT': 'C-01'}, {'TIME': 51226853, 'TEXT': 'C-02'}, {'TIME': 51227623, 'TEXT': 'i-25'}, {'TIME': 51229137, 'TEXT': 'C-05'}, {'TIME': 51229902, 'TEXT': 'C-06'}, {'TIME': 51230655, 'TEXT': 'C-07'}, {'TIME': 51231424, 'TEXT': 'C-08'}, {'TIME': 51232180, 'TEXT': 'C-09'}, {'TIME': 51232931, 'TEXT': 'C-10'}, {'TIME': 51233705, 'TEXT': 'C-01'}, {'TIME': 51234455, 'TEXT': 'C-02'}, {'TIME': 51235213, 'TEXT': 'i-25'}, {'TIME': 51235973, 'TEXT': 'i-30'}, {'TIME': 51236728, 'TEXT': 'C-05'}, {'TIME': 51237495, 'TEXT': 'C-06'}, {'TIME': 51238257, 'TEXT': 'C-07'}, {'TIME': 51239011, 'TEXT': 'C-08'}, {'TIME': 51239781, 'TEXT': 'C-09'}, {'TIME': 51240545, 'TEXT': 'C-10'}, {'TIME': 51241312, 'TEXT': 'C-01'}, {'TIME': 51242073, 'TEXT': 'C-02'}, {'TIME': 51242832, 'TEXT': 'i-25'}, {'TIME': 51243605, 'TEXT': 'i-30'}, {'TIME': 51244376, 'TEXT': 'C-05'}, {'TIME': 51245127, 'TEXT': 'C-06'}, {'TIME': 51245895, 'TEXT': 'C-07'}, {'TIME': 51246661, 'TEXT': 'C-08'}, {'TIME': 51247417, 'TEXT': 'C-09'}, {'TIME': 51248177, 'TEXT': 'C-10'}, {'TIME': 51248937, 'TEXT': 'C-01'}, {'TIME': 51249692, 'TEXT': 'C-02'}, {'TIME': 51250453, 'TEXT': 'i-25'}, {'TIME': 51251219, 'TEXT': 'i-30'}, {'TIME': 51251981, 'TEXT': 'C-05'}, {'TIME': 51252741, 'TEXT': 'C-06'}, {'TIME': 51253510, 'TEXT': 'C-07'}, {'TIME': 51254265, 'TEXT': 'C-08'}, {'TIME': 51255018, 'TEXT': 'C-09'}, {'TIME': 51255791, 'TEXT': 'C-10'}, {'TIME': 51256549, 'TEXT': 'C-01'}, {'TIME': 51257308, 'TEXT': 'C-02'}, {'TIME': 51258063, 'TEXT': 'i-25'}, {'TIME': 51258827, 'TEXT': 'i-30'}, {'TIME': 51259588, 'TEXT': 'C-05'}, {'TIME': 51260353, 'TEXT': 'C-06'}, {'TIME': 51261109, 'TEXT': 'C-07'}, {'TIME': 51261884, 'TEXT': 'C-08'}, {'TIME': 51262630, 'TEXT': 'C-09'}, {'TIME': 51263395, 'TEXT': 'C-10'}, {'TIME': 51264146, 'TEXT': 'C-01'}, {'TIME': 51264912, 'TEXT': 'C-02'}, {'TIME': 51265656, 'TEXT': 'i-25'}, {'TIME': 51266417, 'TEXT': 'i-30'}, {'TIME': 51267186, 'TEXT': 'C-05'}, {'TIME': 51267944, 'TEXT': 'C-06'}, {'TIME': 51268710, 'TEXT': 'C-07'}, {'TIME': 51269468, 'TEXT': 'C-08'}, {'TIME': 51270226, 'TEXT': 'C-09'}, {'TIME': 51270984, 'TEXT': 'C-10'}, {'TIME': 51271742, 'TEXT': 'C-01'}, {'TIME': 51272509, 'TEXT': 'C-02'}, {'TIME': 51273265, 'TEXT': 'i-25'}, {'TIME': 51274031, 'TEXT': 'i-30'}, {'TIME': 51274784, 'TEXT': 'C-05'}, {'TIME': 51275544, 'TEXT': 'C-06'}, {'TIME': 51276316, 'TEXT': 'C-07'}, {'TIME': 51277068, 'TEXT': 'C-08'}, {'TIME': 51277825, 'TEXT': 'C-09'}, {'TIME': 51278582, 'TEXT': 'C-10'}, {'TIME': 51279350, 'TEXT': 'C-01'}, {'TIME': 51280105, 'TEXT': 'C-02'}, {'TIME': 51280876, 'TEXT': 'i-25'}, {'TIME': 51281633, 'TEXT': 'i-30'}, {'TIME': 51282406, 'TEXT': 'C-05'}, {'TIME': 51283164, 'TEXT': 'C-06'}, {'TIME': 51283925, 'TEXT': 'C-07'}, {'TIME': 51284687, 'TEXT': 'C-08'}, {'TIME': 51285447, 'TEXT': 'C-09'}, {'TIME': 51286212, 'TEXT': 'C-10'}, {'TIME': 51286973, 'TEXT': 'C-01'}, {'TIME': 51287739, 'TEXT': 'C-02'}]}
    dictMasterMobInfo = {'C-01': ['TapeName_C-01', [0, 128, 128]], 'C-02': ['TapeName_C-02', [0, 128, 128]], 'C-05': ['TapeName_C-05', [0, 128, 128]], 'C-06': ['TapeName_C-06', [0, 128, 128]], 'C-07': ['TapeName_C-07', [152, 251, 152]], 'C-08': ['TapeName_C-08', [152, 251, 152]], 'C-09': ['TapeName_C-09', [152, 251, 152]], 'C-10': ['TapeName_C-10', [152, 251, 152]], 'i-25': ['TapeName_i-25', [231, 126, 49]], 'i-30': ['TapeName_i-30', [255, 182, 193]], 'PGM': ['TapeName_PGM', [147, 112, 219]]}
    result_dir = "/Users/trevoraylward/Documents/GitHub/_TallyToAAF/data/"

    sequence_name = 'TestTallyLog ' + msToHMS(events["start"]) + ' - ' +msToHMS(events["end"])
    file_name = result_dir + sequence_name + '.aaf'

# Logging
logging.basicConfig(filename=os.path.join(result_dir, 'error.log'), level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)

logger.info("Started AAF")

# g=openos.path.join(result_dir,  "test_events.txt", "w")
# g.write(str(events))
# g.close

# g=openos.path.join(result_dir, "test_dictMasterMobInfo.txt", "w")
# g.write(str(dictMasterMobInfo))
# g.close


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

    attrib_list = comp_mob['MobAttributeList']
    attrib_list.append(f.create.TaggedValue("_COLOR_R", 12000))
    attrib_list.append(f.create.TaggedValue("_COLOR_G", 16000))
    attrib_list.append(f.create.TaggedValue("_COLOR_B", 60000))

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


    for key in dictMasterMobInfo.keys():

        # tape_name = dictMasterMobInfo[key][0] # Tape name from source
        tape_name = dictMasterMobInfo['PGM'][0] # Tape name from PGM


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
        clip_color = dictMasterMobInfo[key][1]
        if clip_color != "":
            attrib_list = master_mob['MobAttributeList']
            attrib_list.append(f.create.TaggedValue("_COLOR_R", convert_8_16bit(clip_color[0])))
            attrib_list.append(f.create.TaggedValue("_COLOR_G", convert_8_16bit(clip_color[1])))
            attrib_list.append(f.create.TaggedValue("_COLOR_B", convert_8_16bit(clip_color[2]))) 

        clip = file_mob.create_source_clip(slot_id=1)


        slot = master_mob.create_picture_slot(frame_rate)
        slot.segment.components.append(clip)

        # dictMobID[key] = master_mob.mob_id
        dictMobID[key] = master_mob
        f.content.mobs.append(master_mob)

# TODO This is the marker section - really just one marker atm
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
    # Range seems to need to be number of tracks required +1
    for i in range(1,3):
        nested_slot = comp_mob.create_timeline_slot(frame_rate)
        nested_slot['PhysicalTrackNumber'].value = i
        nested_scope = f.create.NestedScope()
        nested_slot.segment= nested_scope

        sequence = f.create.Sequence(media_kind="picture")
        nested_scope.slots.append(sequence)
        # SOURCE on V1 with PGM tape name
        if i == 1 :
            nested_slot.name = 'SRC-PGM'
            clip_position = 0
            for j, event in enumerate(events["clips"]):

                clip_start = event['TIME']
                clip_start = msToFrames(clip_start)

                if j < len(events["clips"]) -1:
                    clip_end = events["clips"][j+1]['TIME']
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

        # PGM on V2 with PGM
        if i == 2 :
            nested_slot.name = 'PGM-PGM'
            clip_position = 0
            for j, event in enumerate(events["clips"]):

                clip_start = event['TIME']
                clip_start = msToFrames(clip_start)

                if j < len(events["clips"]) -1:
                    clip_end = events["clips"][j+1]['TIME']
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
    # for i in range(1,5):
    #     nested_slot = comp_mob.create_timeline_slot(frame_rate)
    #     nested_slot['PhysicalTrackNumber'].value = i
    #     nested_slot.name = 'Slot_A_' + str(i)
    #     nested_scope = f.create.NestedScope()
    #     nested_slot.segment= nested_scope

    #     sequence = f.create.Sequence(media_kind="sound")
    #     nested_scope.slots.append(sequence)
    #     comp_fill = f.create.Filler("sound", sequence_length)
    #     sequence.components.append(comp_fill)
logger.info("AAF success")