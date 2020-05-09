import ffmpeg
import subprocess
import os
from enum import Enum
from threading import Thread

_MKV_FILE_PATH_FORMAT = 'D:/1-mkv/{:02d}.mkv'
_SUB_FILE_PATH_FORMAT = 'C\\:\\\\1-sub\\\\{:02d}.ass'

_CONVERTING_FOLDER_PATH_FORMAT = 'C:/2-converting/{:02d}/'
_CONVERTING_VIDEO_NAME_FORMAT = 'video.avc'
_CONVERTING_AUDIO_NAME_FORMAT = 'audio.flac'
_CONVERTED_AUDIO_NAME_FORMAT = 'audio.aac'

_OUTPUT_FILE_PATH_FORMAT = 'C:/3-output/{:02d}.mp4'


class ItemStatus(Enum):
    Waiting = 1
    Processing = 2
    Processed = 3


class Item(object):
    def __init__(self, index):
        self.index = index

        self.extraction = ItemStatus.Waiting
        self.extraction_thread = None

        self.audio_conversion = ItemStatus.Waiting
        self.audio_conversion_thread = None

        self.merging = ItemStatus.Waiting
        self.merging_thread = None
        pass

    def __str__(self):
        return "[index={}, extraction={}, audio={}, merging={}]".format(self.index,
                                                                        self.extraction,
                                                                        self.audio_conversion,
                                                                        self.merging)

    def __repr__(self):
        return self.__str__()


def extract_from_mkv(index):
    print("{} - EXTRACTION...".format(index))
    mkv_file_path = _MKV_FILE_PATH_FORMAT.format(index)
    converting_folder = _CONVERTING_FOLDER_PATH_FORMAT.format(index)
    video_path = converting_folder + _CONVERTING_VIDEO_NAME_FORMAT
    audio_path = converting_folder + _CONVERTING_AUDIO_NAME_FORMAT
    cmd = ['mkvextract',
           mkv_file_path,
           'tracks',
           '0:{}'.format(video_path),
           '1:{}'.format(audio_path)]
    subprocess.run(cmd, stdout=open(os.devnull, 'wb'))
    pass


def convert_audio(index):
    print("{} - EXTRACTION AUDIO".format(index))

    converting_folder = _CONVERTING_FOLDER_PATH_FORMAT.format(index)
    input_audio_path = converting_folder + _CONVERTING_AUDIO_NAME_FORMAT
    output_audio_path = converting_folder + _CONVERTED_AUDIO_NAME_FORMAT
    process = (
        ffmpeg
            .input(input_audio_path)
            .output(output_audio_path, acodec='aac')
    )
    run_process(process)
    pass


def merge_video(index):
    print("{} - EXTRACTION MERGE...".format(index))
    converting_folder = _CONVERTING_FOLDER_PATH_FORMAT.format(index)
    input_video_path = converting_folder + _CONVERTING_VIDEO_NAME_FORMAT
    input_audio_path = converting_folder + _CONVERTING_AUDIO_NAME_FORMAT
    input_sub_path = _SUB_FILE_PATH_FORMAT.format(index)

    output_file_path = _OUTPUT_FILE_PATH_FORMAT.format(index)
    process = (
        ffmpeg
            .input(input_video_path,
                   i=input_audio_path,
                   vsync=0, hwaccel='cuvid',
                   vcodec='h264_cuvid')
            .output(output_file_path,
                    acodec='aac', vcodec='h264_nvenc',
                    crf=10,
                    vf="ass='{}'".format(input_sub_path))
    )
    run_process(process)


def run_process(process):
    process.run(quiet=True, overwrite_output=True)
    # process.run(overwrite_output=True)
    pass


def extraction_runner(item_list):
    __MAX_NUM_THREAD = 3
    num_finished_items = 0
    processing_list = []
    while num_finished_items < len(item_list):
        # Clear completed threads
        for item in processing_list:
            if not item.extraction_thread.is_alive():
                # Mark complete
                item.extraction = ItemStatus.Processed
                # Remove item from current list
                processing_list.remove(item)
                # Increase count
                num_finished_items += 1
                print("{} - EXTRACTION ...".format(item.index))
                pass
            pass

        # Add new threads
        for item in item_list:
            # Stop adding new thread if reaches __MAX_NUM_THREAD
            if len(processing_list) >= __MAX_NUM_THREAD:
                break

            # Add new thread in order
            if item.extraction == ItemStatus.Waiting:
                # Create new thread from item
                thread = Thread(target=extract_from_mkv, args=[item.index])
                thread.start()
                # Add thread
                item.extraction_thread = thread
                # Make item as processing
                item.extraction = ItemStatus.Processing
                # Add item to processing list
                processing_list.append(item)
                pass
        pass
    print("ALL - EXTRACTION finished")
    pass


def convert_audio_runner(item_list):
    num_finished_items = 0
    current_item = item_list[0]
    # New thread
    thread = Thread(target=convert_audio, args=[current_item.index])
    thread.start()
    # Add thread
    current_item.audio_conversion_thread = thread
    # Mark processing
    current_item.audio_conversion = ItemStatus.Processing
    while num_finished_items < len(item_list):

        if not current_item.audio_conversion_thread.is_alive():
            # Mark complete
            current_item.audio_conversion = ItemStatus.Processed
            print("{} - EXTRACTION Audio ...".format(current_item.index))
            # Remove item from current
            current_item = None
            # Increase count
            num_finished_items += 1

            # Start new
            for item in item_list:
                if item.extraction == ItemStatus.Processed and item.audio_conversion == ItemStatus.Waiting:
                    # New thread
                    thread = Thread(target=convert_audio, args=[item.index])
                    thread.start()
                    # Add thread
                    item.audio_conversion_thread = thread
                    # Mark processing
                    item.audio_conversion = ItemStatus.Processing
                    # Set to current
                    current_item = item
                    # Break look up
                    break
                pass
            pass
        pass
    print("ALL - AUDIO finished")
    pass


def main():
    start_index = 1
    end_index = 48
    # items = [Item(i) for i in range(start_index, end_index)]
    # print(items)
    # extraction_thread = Thread(target=extraction_runner, args=[items])
    # extraction_thread.start()
    # audio_conversion_thread = Thread(target=convert_audio_runner, args=[items])
    # audio_conversion_thread.start()
    #
    # while extraction_thread.is_alive() or audio_conversion_thread.is_alive():
    #     pass
    # pass
    for i in range(start_index, end_index):
        extract_from_mkv(i)
        merge_video(i)
        pass
    pass

if __name__ == '__main__':
    main()
    pass
