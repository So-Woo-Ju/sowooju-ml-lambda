from webvtt import WebVTT, Caption
import webvtt
import datetime
import os

def make_vtt(data, userFileName):
    vtt = WebVTT()

    for line in data:
        fmt = '%H:%M:%S.%f'
        start_time = datetime.datetime.fromtimestamp(line['start'], tz=datetime.timezone.utc).strftime(fmt)[:-3]
        end_time = datetime.datetime.fromtimestamp(line['end'], tz=datetime.timezone.utc).strftime(fmt)[:-3]
        caption = Caption(start_time, end_time, line['text'])

        vtt.captions.append(caption)

    os.chdir('/tmp')
    userTempFileSrc = '/tmp/' + userFileName + '-temp.vtt'
    res = vtt.save(userTempFileSrc)

    return userTempFileSrc