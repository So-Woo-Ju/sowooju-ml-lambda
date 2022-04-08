from pydub import AudioSegment
from pydub.silence import detect_silence
from pydub.silence import detect_nonsilent

import ffmpeg
import json
import urllib.parse

import tensorflow as tf
import tensorflow_io as tfio
import boto3
import os
import spleeter

s3 = boto3.client('s3')
filter_classifier_model = tf.saved_model.load('classifier-yamnet')

# adjust target amplitude
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)

# 추임새/비추임새 판정
def load_wav_16k_mono(filename):
    """ Load a WAV file, convert it to a float tensor, resample to 16 kHz single-channel audio. """
    file_contents = tf.io.read_file(filename)
    wav, sample_rate = tf.audio.decode_wav(
          file_contents,
          desired_channels=1)
    wav = tf.squeeze(wav, axis=-1)
    sample_rate = tf.cast(sample_rate, dtype=tf.int64)
    wav = tfio.audio.resample(wav, rate_in=sample_rate, rate_out=16000)
    return wav

# 추임새 종류 판별
def predict_filter_type(audio_file):
  # 클래스 분류를 위한 임시 음성 파일 생성
  audio_file.export("/tmp/tmp.wav", format="wav")

  ## 경로 재설정 필요
  testing_wav_data = load_wav_16k_mono("/tmp/tmp.wav")

  my_classes = ['engine', 'breathing', 'dog', 'laughing', 'background_sound']

  reloaded_results = filter_classifier_model(testing_wav_data)

  return my_classes[tf.argmax(reloaded_results)]

def create_json(audio_file):
  intervals_jsons = []

  min_silence_length = 70
  intervals = detect_nonsilent(audio_file,
                               min_silence_len=min_silence_length,
                               silence_thresh=-32.64)
  
  if intervals[0][0] != 0:
    intervals_jsons.append({'start':0,'end':intervals[0][0]/1000,'tag':'침묵'}) 
    
  non_silence_start = intervals[0][0]
  before_silence_start = intervals[0][1]

  for interval in intervals:
    interval_audio = audio_file[interval[0]:interval[1]]

    if (interval[0] - before_silence_start) >= 1000:
      intervals_jsons.append({'start':non_silence_start/1000,'end':(before_silence_start+200)/1000,'tag':'비침묵'}) 
      non_silence_start = interval[0]-200
      intervals_jsons.append({'start':before_silence_start/1000,'end':interval[0]/1000,'tag':'침묵'}) 
    before_silence_start = interval[1]

  if non_silence_start != len(audio_file):
    intervals_jsons.append({'start':non_silence_start/1000,'end':len(audio_file)/1000,'tag':'비침묵'})

  return intervals_jsons

def sound_with_json(audio_file, json):
  nonsilent_json = []
  for j in json:
    if (j['tag'] == '비침묵'):
      if (j['end'] - j['start'] <= 3):
        nonsilent_json.append(j)
      else:
        start = j['start']
        end = j['end']
        while(end - start > 3):
          tmp = {}
          tmp['start'] = start
          tmp['end'] = start + 3
          tmp['tag'] = '비침묵'
          nonsilent_json.append(tmp)
          start = tmp['end']
                    
  category = []
  for idx, json in enumerate(nonsilent_json):
    cut_audio = audio_file[json['start']*1000:json['end']*1000]
    predict = predict_filter_type(cut_audio)
    category.append(predict)

  for idx, p in enumerate(category):
    nonsilent_json[idx]['tag'] = category[idx]   

  for j in nonsilent_json:
    print(j)

  return {"결과":nonsilent_json}

def make_transcript(audio_file_path):

  audio = AudioSegment.from_file(audio_file_path)
  normalized_audio = match_target_amplitude(audio, -20.0)
  intervals_jsons = create_json(normalized_audio) # 구간, 태그 정보를 담은 Json 형태의 Array 반환
  transcript_json = sound_with_json(normalized_audio, intervals_jsons) # JSON을 가지고 STT한 결과 추가
  return transcript_json


# lambda 실행 시, lambda_handler가 먼저 실행됩니다.
def lambda_handler(event, context):

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        s3.download_file(bucket, key, '/tmp/temp.mp3')
        src = "/tmp/temp.mp3"
        
        spleeter separate -p spleeter:2stems -o output src
        accompanimentSrc = 'output/temp/accompaniment.wav'
        # vocalsSrc = 
        
        result_json = json.dumps(make_transcript(accompanimentSrc))
        return result_json
    except Exception as e:
        print(e)
        raise e