import base64, os, sys, re
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
import os
import sys
import subprocess
from PIL import Image
from io import BytesIO


def resize_image(img):
    max_width = 315
    max_height = 405
    width, height = img.size
    # Calculate the aspect ratio
    aspect_ratio = width / height
    # Check if the image needs to be resized
    if width > max_width or height > max_height:
        # Calculate the new size while maintaining the aspect ratio
        if width >= height:
            ratio = max_width / width
        else:
            ratio = max_height / height
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        # Resize the image
        img = img.resize((new_width, new_height))
    return img

def lambda_handler3(event):
    text = event["data"]
    s3 = event["s3"]
    key = event["key"]
    media_bucket = event["media_bucket"]
    
    res = s3.get_object(Bucket="to-html-py", Key="qa/images/frame.png")
    border_img = Image.open(BytesIO(res['Body'].read()))
    count = 0
    for img in re.findall(r'<img\s+[^>]*src\s*=\s*["\']([^"\']+)["\'][^>]*>', text):
        count += 1
        url = ""
        base64_str = img.split(',')[1]
        img_data = base64.b64decode(base64_str)
    
        img_data = Image.open(BytesIO(img_data))
        # Optimize the image
        img_data_o = img_data.convert('RGB')
        optimized_image = BytesIO()
        img_data_o.save(optimized_image, format='PNG', optimize=True, quality=70)
        optimized_image.seek(0)
        # Upload to S3
        s3.put_object(Body=optimized_image, Bucket=media_bucket, Key=key+f"_{count}.png")
    
        url = key+f"_{count}.png"
        # replace src with url
        text = text.replace('src="{}"'.format(img), 'src="{}"'.format(url))
    
    image = resize_image(img_data)

    merged_img = Image.new(image.mode, border_img.size, (255, 255, 255))
    
    x_offset = (border_img.width - image.width) // 2
    y_offset = (border_img.height - image.height) // 2
    
    merged_img.paste(image, (x_offset, y_offset))
    merged_img.paste(border_img, (0, 0), border_img)
    
    last_img = BytesIO()
    merged_img.save(last_img, format='PNG')
    last_img.seek(0)
    
    s3.put_object(Body = last_img, Bucket=media_bucket, Key=f"{key}_m.png")
    m_url = f"https://{media_bucket}/{key}_m.png"
    return {
        "data": text,
        "url": m_url,
        "img_key": f"{key}_m.png"
    }