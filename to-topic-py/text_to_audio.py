import json, boto3, os, re, base64, random, string, subprocess
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing

def split_string_by_words(string):
    # Split the string into a list of words
    words = string.split()
    # Initialize the output list
    output = []
    # Loop through the list of words and concatenate them into strings of up to 230 words
    current_string = ""
    for word in words:
        # Add the current word and a space to the current string
        current_string += word + " "
        # If the length of the current string is greater than 230 words, add it to the output list and start a new string
        if len(current_string.split()) > 230:
            output.append(current_string.strip())
            current_string = ""
    # Add any remaining words to the output list
    if current_string:
        output.append(current_string.strip())
    return output

def convert_to_audio(text, polly):
    try:
        response = polly.synthesize_speech(
            Engine="neural",
            LanguageCode="en-US",
            Text=text,
            OutputFormat="mp3",
            VoiceId="Matthew"
        )

    except (BotoCoreError, ClientError) as error:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(error)})
        }

    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            return stream.read()
        
    else:
        print("Could not stream audio")


def lambda_handler_2(event):
    mytext = event['mytext']
    media_bucket = event["bucket"]
    aud_key = event["aud_key"]
    
    session = Session(
        aws_access_key_id = os.environ["aws_access_key_id"],
        aws_secret_access_key = os.environ["aws_secret_access_key"],
        region_name = os.environ["region"]
    )
    polly = session.client("polly")
    s3 = session.client("s3")
    
    text_arr = mytext.split(" ")
    audio_files_bytes = []
    
    if len(text_arr) > 230:
        texts_arr = split_string_by_words(mytext)
        for x in texts_arr:
            audio_files_bytes.append(convert_to_audio(x, polly))
    else:
        audio_files_bytes.append(convert_to_audio(mytext, polly))

    merged_bytes = bytes()
    
    for audio_bytes in audio_files_bytes:
        merged_bytes += audio_bytes
        
    res = s3.put_object(Bucket=media_bucket, Key=aud_key, Body=merged_bytes)
    # if res["HTTPStatusCode"] == 200:
    url = f"https://{media_bucket}/{aud_key}"
    return {
        'statusCode': 200,
        "url": url
    }