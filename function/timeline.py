import requests
import json
import os

def invoke_clova(s3VideoUrl):
  text = ClovaSpeechClient().req_url(s3VideoUrl, language="ko-KR", completion="sync")
  return json.loads(text)


def preprocess_clova(clova):
  clova_timeline = []
  for i in clova['segments']:
    start = i['start'] * 0.001
    end = i['end'] * 0.001
    text = i['text']
    clova_timeline.append({'start': start, 'end': end, 'tag' : text})
  return clova_timeline
  

def make_timeline(background_timeline, clova_timeline):
  result_timeline_json = []
  background_timeline_idx = 0
  clova_timeline_idx = 0
  start = 0
  pre_start = 0
  end = 0
  while(True):
    text = ''
    if(background_timeline[background_timeline_idx]['start'] < clova_timeline[clova_timeline_idx]['start']):
      start = background_timeline[background_timeline_idx]['start']
    else:
      start = clova_timeline[clova_timeline_idx]['start']

    if(background_timeline[background_timeline_idx]['end'] < clova_timeline[clova_timeline_idx]['end']):
      end = background_timeline[background_timeline_idx]['end']
      if(end < clova_timeline[clova_timeline_idx]['start']):
        text = '(' + background_timeline[background_timeline_idx]['tag'] + ')'
      else:
        text = '(' + background_timeline[background_timeline_idx]['tag'] + ')' + clova_timeline[clova_timeline_idx]['tag']
      background_timeline_idx = background_timeline_idx + 1
    else:
      end = clova_timeline[clova_timeline_idx]['end']
      if(end < background_timeline[background_timeline_idx]['start']):
        text = clova_timeline[clova_timeline_idx]['tag']
      else:
        text = '(' + background_timeline[background_timeline_idx]['tag'] + ')' + clova_timeline[clova_timeline_idx]['tag']
      clova_timeline_idx = clova_timeline_idx + 1
    pre_start = start

    result_timeline_json.append({'start': start, 'end': end, 'text' : text})
    if(background_timeline_idx == len(background_timeline) or clova_timeline_idx == len(clova_timeline)):
      break

  if(background_timeline_idx < len(background_timeline)):
    for i in range(background_timeline_idx, len(background_timeline)):
      if(end > background_timeline[i]['start']):
        continue
      result_timeline_json.append({'start': background_timeline[i]['start'], 'end': background_timeline[i]['end'], 'text' : '(' + background_timeline[i]['tag'] + ')'})

  if(clova_timeline_idx < len(clova_timeline)):
    for i in range(clova_timeline_idx, len(clova_timeline)):
      if(end > clova_timeline[i]['start']):
        continue
      result_timeline_json.append({'start': clova_timeline[i]['start'], 'end': clova_timeline[i]['end'], 'text' : clova_timeline[i]['tag']})
  
  for i in range(1, len(result_timeline_json)):
    if(result_timeline_json[i - 1]['end'] > result_timeline_json[i]['start']):
      result_timeline_json[i]['start'] = result_timeline_json[i - 1]['end']

  result_timeline_json_delete_overlap = []
  for i in range(len(result_timeline_json) - 1):
    if(result_timeline_json[i]['text'] == ""):
      continue
    if (result_timeline_json[i]['end'] != result_timeline_json[i+1]['start']):
      result_timeline_json_delete_overlap.append(result_timeline_json[i])
    else:
      if (result_timeline_json[i]['text'] != result_timeline_json[i+1]['text']):
        result_timeline_json_delete_overlap.append(result_timeline_json[i])
      else:
        result_timeline_json[i+1]['start'] = result_timeline_json[i]['start']
  result_timeline_json_delete_overlap.append(result_timeline_json[len(result_timeline_json) - 1])

  return json.dumps(result_timeline_json_delete_overlap, ensure_ascii=False)


class ClovaSpeechClient:
      # Clova Speech invoke URL
    invoke_url = os.environ['invoke_url']

    # Clova Speech secret key
    secret = os.environ['secret']

    def req_url(self, url, language, completion, callback=None, userdata=None, forbiddens=None, boostings=None, sttEnable=True,
                wordAlignment=True, fullText=True, script='', diarization=None, keywordExtraction=None, groupByAudio=False):
        # 호출 예시
        # ClovaSpeechClient().req_url("http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4", "ko-KR", "sync")

        request_body = {
            'url': url, 
            #url 넣어줄때 s3 접근 가능 url 을 넣어줄 것
            # res = s3_client.list_objects_v2(Bucket=bucket, Prefix=path, MaxKeys=1)
            # 'Contents' in res
            # json_value = json.dumps(json.load(res['Body']))
            'language': language,
            # 'language': 'ko-KR',
            # 'language': 'en-US',
            'completion': completion,
            'callback': callback,
            'userdata': userdata,
            'sttEnable': sttEnable,
            'wordAlignment': wordAlignment,
            'fullText': fullText,
            'script': script,
            'forbiddens': forbiddens,
            'boostings': boostings,
            'diarization': diarization,
            'keywordExtraction': keywordExtraction,
            'groupByAudio': groupByAudio,
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'Content-Type': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self.secret
        }
        res = requests.post(headers=headers,
                            url=self.invoke_url + '/recognizer/url',
                            data=json.dumps(request_body).encode('UTF-8'))
        return res.text