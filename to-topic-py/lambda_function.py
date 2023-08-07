import json, requests, boto3, os, re, base64, random, string, subprocess, io
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from text_to_audio import lambda_handler_2
from PIL import Image

def lambda_handler(event, context):
    
    session = Session(
      aws_access_key_id=os.environ['aws_access_key_id'], 
      aws_secret_access_key=os.environ['aws_secret_access_key'], 
      region_name=os.environ['region']
    )
    s3 = session.client("s3")
    polly = session.client("polly")
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    
    folder_name = key.split('/')[0]
    
    letters = string.ascii_letters + string.digits
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read().decode('utf-8')
    temp_img_bucket = "to-html-py"
    if folder_name == "qa":
      add_topic_api = os.environ['qa_add_topic_api']
      update_topic_api = os.environ['qa_update_topic_api']
      media_bucket = "qa-media.hazwoper-osha.com"
      
    elif folder_name == "live":
      add_topic_api = os.environ['live_add_topic_api']
      update_topic_api = os.environ['live_update_topic_api']
      media_bucket = "media.hazwoper-osha.com"
    
    img_key = "assets/images/{}"
    aud_key = "assets/audios/{}"
    
    img_match = re.search(r'<img\s+[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>', data)
    id_arr = key.split('_')
    course_id, module_id, lesson_id = id_arr[1], id_arr[2], id_arr[3]
    pos = id_arr[4].split('.')[0]
    
    f_h1 = r"<h1>(?:<[^>]+>)*(.*?)(?:<[^>]+>)*</h1>"

    # Use regex to search for the first h1 tag and extract its text
    match = re.search(f_h1, data)
    name = match.group(1)
    
    add_topic_payload = {
      "topic_name": name,
      "lesson_id": f"{lesson_id}",
      "module_id": f"{module_id}",
      "course_id": f"{course_id}",
      "level": 3,
      "position": int(pos)
    }
    
    topic_data_payload = {
      "id": "",
      "topic_data": {
        "id": "",
        "name": name,
        "leftDiv": {
          "audio": {
            "isAudio": False,
            "audioURL": "",
            "audioFile": "",
            "audioName": ""
          },
          "image": {
            "isImage": False,
            "imageURL": "",
            "imageName": "",
            "imageFile": ""
          },
          "video": {
            "isVideo": False,
            "videoURL": "",
            "videoName": "",
            "videoFile": ""
          },
          "width": "col-12",
          "editor": "",
          "editorHtml": "",
          "captureTime": [],
          "editorSaved": "",
          "mediaDuration": 80.143673,
          "editorHtmlSaved": "",
          "isEditorSelected": True,
          "mediaCurrentTime": 0
        },
        "datatime": "0",
        "lessonId": f"{lesson_id}",
        "moduleId": f"{module_id}",
        "rightDiv": {
          "audio": {
            "isAudio": False,
            "audioURL": "",
            "audioFile": "",
            "audioName": ""
          },
          "image": {
            "isImage": False,
            "imageURL": "",
            "imageFile": "",
            "imageName": ""
          },
          "video": {
            "isVideo": False,
            "videoURL": "",
            "videoFile": "",
            "videoName": ""
          },
          "width": "col-12",
          "editor": "",
          "editorHtml": "",
          "captureTime": [],
          "editorSaved": "",
          "mediaDuration": 0,
          "editorHtmlSaved": "",
          "isEditorSelected": False,
          "mediaCurrentTime": 0
        },
        "topicDuration": 0,
        "headingContent": "",
        "selectedTemplate": 1
      },
      "topic_duration": "0"
    }
    
    result_str = ''.join(random.choice(letters) for i in range(10))
    if img_match:
      obj = {
        "data": data,
        "key": img_key.format(f"{course_id}_{module_id}_{lesson_id}_{pos}_{result_str}"),
        "media_bucket": media_bucket,
        "s3": s3
      }
      frame_reg = r'<h6\b[^>]*>(?:<img\s+[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>)</h6>'
      frame_match = re.findall(frame_reg, data)
      frame_data = ''
      if frame_match:
        frame_data = base64.b64decode(frame_match[0].split(',')[1])
        data = re.sub(frame_reg, '', data)
        
      t_img_key = f"qa/base64_images/{course_id}_{module_id}_{lesson_id}_{pos}_{result_str}"
      for i, img in enumerate(re.findall(r'<img\s+[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>', data)):
        base64_str = img.split(',')[1]
        img_data = base64.b64decode(base64_str)
        
        url =  f"https://{media_bucket}/" + img_key.format(f"{course_id}_{module_id}_{lesson_id}_{pos}_{result_str}")+f"_{i}.png"
        # replace src with url
        data = data.replace('src="{}"'.format(img), 'src="{}"'.format(url))
        s3.put_object(Body=img_data, Bucket = temp_img_bucket, Key= t_img_key+f"_{i}.png", ContentType='image/png')
      
      # for frame image
      if frame_data:
        img_data = frame_data
        s3.put_object(Body=img_data, Bucket = temp_img_bucket, Key= t_img_key+f"_m.png", ContentType='image/png')
        t_key = img_key.format(f"{course_id}_{module_id}_{lesson_id}_{pos}_{result_str}")
        data, url, img_key = data, f"https://{media_bucket}/{t_key}_m.png", t_key+"_m.png"
      else:
        img_key = url = ""

      topic_data_payload['topic_data']['rightDiv']['image']['isImage'] = True
      topic_data_payload['topic_data']['rightDiv']['image']["imageURL"] = topic_data_payload['topic_data']['rightDiv']['image']["imageFile"] = url
      topic_data_payload['topic_data']['rightDiv']['image']["imageName"] = img_key
      
      topic_data_payload['topic_data']['leftDiv']['image']['isImage'] = True
      topic_data_payload['topic_data']['leftDiv']['image']["imageURL"] = topic_data_payload['topic_data']['leftDiv']['image']["imageFile"] = url
      topic_data_payload['topic_data']['leftDiv']['image']["imageName"] = img_key
    
    data1 = str(data)
    data = re.sub(f_h1, '', data1)
    topic_data_payload['topic_data']['leftDiv']['editor'] = topic_data_payload['topic_data']['leftDiv']['editorSaved'] = topic_data_payload['topic_data']['rightDiv']['editor'] = topic_data_payload['topic_data']['rightDiv']['editorSaved'] = data
    n_line_p = re.compile(r"</p>")
    cleanr = re.compile('<.*?>')
    n_line = re.compile(r"</li>|</p>|</h[234]>")
    html = re.sub(f_h1, '', data1)
    html = n_line.sub("\n", html)
    text = re.sub(cleanr, '', html)
    text = re.sub(r'<img[^>]+>', '', text)
    
    split_text = re.split(r'(?<!\d)\.(?!\d\s)|(?<=\d)\.(?=\s\d)', text)
    res_text = []
    
    for x in split_text:
      sub_str = re.split(r'[:;\n?!]', x)
      res_text.extend(sub_str)
    res_text = list(filter(None, res_text))
    text = ". ".join(res_text)
      
    text = name.strip()+". "+text
    # if folder_name == "qa":
    text = text.replace(" etc.", " etcetera.")
    
    aud_key = f"assets/audios/{course_id}_{module_id}_{lesson_id}_{pos}_{result_str}.mp3"
    ret = lambda_handler_2({
      "mytext": text,
      "bucket": media_bucket,
      "aud_key": aud_key
    })
    
    if ret["statusCode"] == 200:
      topic_data_payload['topic_data']['leftDiv']['audio']['isAudio'] = True
      topic_data_payload['topic_data']['leftDiv']['audio']["audioURL"] = topic_data_payload['topic_data']['leftDiv']['audio']["audioFile"] = ret["url"]
      topic_data_payload['topic_data']['leftDiv']['audio']["audioName"] = aud_key
    else:
      return {
        "error":"error"
      }
    try:
      res1 = requests.post(add_topic_api, json=add_topic_payload, verify=False)
      res1.raise_for_status()
      t_id = res1.json()['topic_id']
      topic_data_payload['id'] = t_id
      topic_data_payload['topic_data']['id'] = t_id
      
      res2 = requests.post(update_topic_api, json=topic_data_payload, verify=False)
      res2.raise_for_status()
      
      s3.delete_object(Bucket=bucket, Key=key)
      return {
        'statusCode1': res1.status_code,
        'statusCode2': res2.status_code,
        "text":text
      }
    except requests.exceptions.RequestException as e:
      return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
      }
  