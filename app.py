from spleeter.separator import Separator

from function.spleeter import make_transcript
from function.timeline import invoke_clova
from function.timeline import preprocess_clova
from function.timeline import make_timeline
from function.caption import make_vtt
from function.thumbnail import make_thumbnail

import json
import urllib.parse
import requests

import boto3
import os

s3 = boto3.client('s3')

# lambda 실행 시, lambda_handler가 먼저 실행됩니다.
def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
      userFile = key
      userFileName = key.split('.')[0]
      thumbnail_s3_bucket = os.environ['thumbnail_s3_bucket']
      text_s3_bucket = os.environ['text_s3_bucket']
      caption_s3_bucket = os.environ['caption_s3_bucket']

      # 메세지큐에 넣을 결과 url
      userId = key.split('-')[0]
      s3VideoUrl = 'https://' + bucket + '.s3.ap-northeast-2.amazonaws.com/' + key
      s3ThumbnailUrl = 'https://' + caption_s3_bucket + '.s3.ap-northeast-2.amazonaws.com/' + userFileName + '.jpg'
      s3TextUrl = 'https://' + text_s3_bucket + '.s3.ap-northeast-2.amazonaws.com/' + userFileName + ".json"
      s3CaptionUrl = 'https://' + caption_s3_bucket + '.s3.ap-northeast-2.amazonaws.com/' + userFileName + ".vtt"

      # 메세지큐 전송
      message = {
        "user" : userId,
        "videoUrl" : s3VideoUrl,
        "captionUrl" : s3CaptionUrl,
        "textUrl" : s3TextUrl,
        "thumbnailUrl" : s3ThumbnailUrl
      }
  
      url = 'https://api.so-woo-ju.com/api/v1/media/s3-url'
      response = requests.post(url, data = message)

      # video bucket에서 비디오 파일 다운로드
      s3.download_file(bucket, key, '/tmp/' + userFile)

      # 스프리터로 음원파일 분리
      os.chdir('/tmp')
      separator = Separator("spleeter:2stems") 
      separator.separate_to_file(userFile, "")

      # thumbanil 생성
      thumbnail = make_thumbnail(userFile, userFileName)

      os.chdir('/var/task')                                         
      accompanimentSrc = '/tmp/' + userFileName + '/accompaniment.wav'
      vocalsSrc = '/tmp/' + userFileName + '/vocals.wav'

      # 분리된 배경음악 타임라인 추출
      background_timeline = make_transcript(accompanimentSrc, userFileName)

      # 스플리터로 인해 생성된 파일 제거
      os.remove('/tmp/' + userFile)
      os.remove(accompanimentSrc)
      os.remove(vocalsSrc)
      os.rmdir('/tmp/' + userFileName)

      # 클로바 호출 및 데이터 전처리 및 타임라인 추출
      clova = invoke_clova(s3VideoUrl)
      clova_timeline = preprocess_clova(clova)

      # 클로바와 배경음악 타임라인 정리하는 코드
      timeline_json = make_timeline(background_timeline, clova_timeline)

      # vtt 파일 생성
      timeline = json.loads(timeline_json)
      caption = make_vtt(timeline, userFileName)

      # 결과 text bucket에 저장
      s3.upload_file(thumbnail, thumbnail_s3_bucket, userFileName + ".jpg")
      s3.put_object(Body=timeline_json, Bucket=text_s3_bucket, Key=userFileName + ".json")
      s3.upload_file(caption, caption_s3_bucket, userFileName + ".vtt")

      os.remove(thumbnail)
      os.remove(caption)

      return True
      
    except Exception as e:
      print(e)
      raise e
