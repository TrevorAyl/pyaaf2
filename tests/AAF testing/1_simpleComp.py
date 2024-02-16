import aaf2
import os
import random
import math

file_name = os.path.splitext(os.path.basename(__file__))
frame_rate = 50
sequence_start = 10*60*60*frame_rate # 10:00:00:00
sequence_length = 1*60*60*frame_rate # 1 hour
num_v_tracks = 4
num_a_tracks = 5
hour_num = random.randrange(1,23)
tape_name = 'tapeName_' + str(hour_num)

with aaf2.open(file_name[0] + ".aaf", 'w') as f:

    # Master Mob = Master Clip in Avid???
    master_mob = f.create.MasterMob("MasterMob_1")
    # Add a clip color
    master_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_R", 0*256))
    master_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_G", 0*256))
    master_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_B", 200*256))  

    f.content.mobs.append(master_mob)

    # Comp Mob = Sequence in Avid
    comp_mob = f.create.CompositionMob("CompositionMob")
    # Add a clip color
    comp_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_R", 200*256))
    comp_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_G", 0*256))
    comp_mob.mobattributelist.append(f.create.TaggedValue("_COLOR_B", 200*256))  
    f.content.mobs.append(comp_mob)

    # Create a TimelineMobSlot with a Timecode Segment for the start timecode
    tc_segment = f.create.Timecode(frame_rate)
    tc_segment.start = sequence_start
    tc_slot = comp_mob.create_timeline_slot(edit_rate=frame_rate)
    tc_slot.segment = tc_segment



    # lets also create a tape so we can add timecode (optional)
    tape_mob = f.create.SourceMob()
    f.content.mobs.append(tape_mob)

    tape_start_time = frame_rate * hour_num * 60 * 60 # 1 hour

    tape_slot, tape_timecode_slot = tape_mob.create_tape_slots(tape_name, frame_rate, frame_rate)        
    
    # set start time for clip
    tape_timecode_slot.segment.start = tape_start_time

    #Reduces from default 12 hours
    tape_slot.segment.length = sequence_length

    tape_clip = tape_mob.create_source_clip(slot_id = 1)
    tape_clip.length = sequence_length
    
    slot = master_mob.create_picture_slot(frame_rate)
    slot.segment.components.append(tape_clip)



    # Nested slots are multiple video tracks in the sequence
    for i in range(1,num_v_tracks+1):
        nested_slot = comp_mob.create_timeline_slot(frame_rate)
        nested_slot['PhysicalTrackNumber'].value = i
        nested_slot.name = 'Slot_V_' + str(i)
        nested_scope = f.create.NestedScope()
        nested_slot.segment= nested_scope

        sequence = f.create.Sequence(media_kind="picture")
        nested_scope.slots.append(sequence)
        comp_fill = f.create.Filler("picture", math.floor(i*100/3))
        sequence.components.append(comp_fill)
        for j in range(0,9):
            mm_clip = master_mob.create_source_clip(slot_id=1, start=100*j, length=100)
            sequence.components.append(mm_clip)


    for i in range(1,num_a_tracks+1):
        nested_slot = comp_mob.create_timeline_slot(frame_rate)
        nested_slot['PhysicalTrackNumber'].value = i
        nested_slot.name = 'Slot_A_' + str(i)
        nested_scope = f.create.NestedScope()
        nested_slot.segment= nested_scope

        sequence = f.create.Sequence(media_kind="sound")
        nested_scope.slots.append(sequence)
        comp_fill = f.create.Filler("sound", sequence_length)
        sequence.components.append(comp_fill)



    # print(master_mob.dump())

    # # now finally import the generated media
    # mob.import_dnxhd_essence("sample.dnxhd", edit_rate, tape_clip)
    # mob.import_audio_essence("sample.wav", edit_rate)