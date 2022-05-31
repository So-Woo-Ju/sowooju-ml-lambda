import os
import spleeter
import tensorflow as tf
import tensorflow_io as tfio

from spleeter.separator import Separator
from pydub import AudioSegment
from pydub.silence import detect_silence
from pydub.silence import detect_nonsilent

filter_classifier_model = tf.saved_model.load('trained-model/classifier-yamnet')

# adjust target amplitude
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)
    

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
def predict_filter_type(audio_file, fileName):
  # 클래스 분류를 위한 임시 음성 파일 생성
  userTempFileSrc = "/tmp/" + fileName + "-temp.wav"
  audio_file.export(userTempFileSrc, format="wav")

  testing_wav_data = load_wav_16k_mono(userTempFileSrc)

  my_classes = ['engine', 'breathing', 'dog', 'laughing', 'clock_tick', 'door_wood_knock', 'keyboard_typing', 'siren', 'footsteps', 'rain', 'thunderstorm', 'wind', 'clock_alarm', 'cat', 'background_sound']

  reloaded_results = filter_classifier_model(testing_wav_data)
  os.remove(userTempFileSrc)

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


def sound_with_json(audio_file, json, fileName):
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
    predict = predict_filter_type(cut_audio, fileName)
    category.append(predict)

  for idx, p in enumerate(category):
    nonsilent_json[idx]['tag'] = category[idx]   

  # 같은 태그 합치는 코드
  final_json = []
  for i in range(len(nonsilent_json) - 1):
    if (nonsilent_json[i]['end'] != nonsilent_json[i+1]['start']):
      final_json.append(nonsilent_json[i])
    else:
      if (nonsilent_json[i]['tag'] != nonsilent_json[i+1]['tag']):
        final_json.append(nonsilent_json[i])
      else:
        nonsilent_json[i+1]['start'] = nonsilent_json[i]['start']
  final_json.append(nonsilent_json[len(nonsilent_json) - 1])
  
  final_json_delete_background_sound = []
  tag = {'engine': "엔진소리가 들린다", 'breathing': "숨쉬는 소리가 들린다", 'dog': "개가 짖고 있다", 'laughing': "사람이 웃고 있다", 'clock_tick': "시계 소리가 들린다", 'door_wood_knock': "노크 소리가 들린다", 'keyboard_typing': "키보드 타이핑하는 소리", 'siren': "사이렌 소리", "footsteps": '발자국 소리가 들린다', 'rain': "빗소리가 들린다",
  'thunderstorm': "천둥 소리가 들린다", 'wind': "바람 소리", 'clock_alarm': "알람이 울린다", 'cat': "고양이 울음 소리가 들린다"}
  'engine', 'breathing', 'dog', 'laughing', 'clock_tick', 'door_wood_knock', 'keyboard_typing', 'siren', 'footsteps', 'rain', 'thunderstorm', 'wind', 'clock_alarm', 'cat', 'background_sound'
  for i in final_json:
    if(i['tag'] != 'background_sound'):
      final_json_delete_background_sound.append(i)

  for i in final_json_delete_background_sound:
    i['tag'] = tag[i['tag']]

  return final_json_delete_background_sound


def make_transcript(audio_file_path, fileName):
  audio = AudioSegment.from_file(audio_file_path)
  normalized_audio = match_target_amplitude(audio, -20.0)
  intervals_jsons = create_json(normalized_audio) # 구간, 태그 정보를 담은 Json 형태의 Array 반환
  transcript_json = sound_with_json(normalized_audio, intervals_jsons, fileName) # JSON을 가지고 STT한 결과 추가
  return transcript_json