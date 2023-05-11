import json, mammoth, boto3, io, os
from bs4 import BeautifulSoup

def lambda_handler(event, context):
    # TODO implement
    s3 = boto3.client(
        's3', 
        aws_access_key_id=os.environ['aws_access_key_id'], 
        aws_secret_access_key=os.environ['aws_secret_access_key'], 
        region_name=os.environ['region']
    )
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    folder_name = key.split('/')[0]
    key2 = folder_name + '/title/'+key.split('/')[2].split('.')[0]
    # Read the file from S3 in binary mode
    response = s3.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    rs = io.BytesIO(data)
    result = mammoth.convert_to_html(rs)
    html = result.value  # The generated HTML
    messages = result.messages  # Any messages,
    # print(html)
    html_doc = (
        '<!DOCTYPE html><html><head><meta charset="utf-8"/></head><body>'
        + html
        + "</body></html>"
    )
    # Parse the HTML document using BeautifulSoup
    soup = BeautifulSoup(html_doc, 'html.parser')
    # Find all the h1 tags in the document
    h1_tags = soup.find_all('h1')
    # Split the document into multiple documents based on the h1 tags
    for i, h1_tag in enumerate(h1_tags):
        # Create a new BeautifulSoup object for the new document
        new_soup = BeautifulSoup(str(h1_tag), 'html.parser')
        # Find all the tags between the current h1 tag and the next h1 tag
        next_h1_tag = h1_tags[i+1] if i+1 < len(h1_tags) else None
        tags_between_h1_tags = []
        current_tag = h1_tag.next_sibling
        while current_tag and current_tag != next_h1_tag:
            tags_between_h1_tags.append(current_tag)
            current_tag = current_tag.next_sibling
        # Add the tags between the h1 tags to the new document
        for tag in tags_between_h1_tags:
            new_soup.append(tag)

        b_new_soup = bytes(str(new_soup), 'utf-8')
        res = s3.put_object(Bucket=bucket, Key=f"{key2}_{i}.html", Body=b_new_soup)
    s3.delete_object(Bucket=bucket, Key=key)
    # Return a response
    return {
        'statusCode': 200,
        'result': json.dumps(res)
    }
