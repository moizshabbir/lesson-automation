# Lambda Functions for Converting Docx to HTML and then generating a topic with audio and images.

This repository contains two AWS Lambda functions: `to-html-py` and `to-topic-py`. These functions are designed to work together to convert Docx files to HTML, generate topic from the HTML content. 

## `to-html-py`

The `to-html-py` function is responsible for converting Docx files to multiple HTML files based on the `h1` tags in the document. Each HTML file contains the content of a single `h1` tag and is saved to an S3 bucket. The function is triggered when a new Docx file is uploaded to the input S3 bucket.

### Prerequisites

- Python 3.9 or later
- AWS account with permissions to create Lambda functions and S3 buckets

### Installation

1. Clone this repository to your local machine
2. Create an S3 bucket to store the input Docx files
3. Create an S3 bucket to store the output HTML files
4. Create a new Lambda function in your AWS account
5. Upload the `to-html-py` code to the Lambda function
6. Configure the Lambda function to trigger on S3 bucket uploads to the input bucket
7. Set environment variables for the input and output S3 bucket names

### Usage

1. Upload a Docx file to the input S3 bucket
2. Wait for the `to-html-py` function to process the file
3. Check the output S3 bucket for the converted HTML files

## `to-topic-py`

The `to-topic-py` function is responsible for generating audio from the HTML content, saving all base64-encoded images to the output S3 bucket, replacing the image base64-encoded src tags with the new S3 URLs, and calling an external topic-update API with the modified HTML and audio files. The function is triggered when a new HTML file is uploaded to the output S3 bucket.

### Prerequisites

- Python 3.9 or later
- AWS account with permissions to create Lambda functions, S3 buckets, and access to the external API

### Installation

1. Clone this repository to your local machine
2. Create an S3 bucket to store the output HTML and audio files
3. Create a new Lambda function in your AWS account
4. Upload the `to-topic-py` code to the Lambda function
5. Configure the Lambda function to trigger on S3 bucket uploads to the output bucket
6. Set environment variables for the output S3 bucket name and the API endpoint URL

### Usage

1. Wait for the `to-html-py` function to process the Docx file and generate the HTML files
2. Upload the HTML files to the output S3 bucket
3. Wait for the `to-topic-py` function to process the HTML files and generate the audio and modified HTML files
4. Check the output S3 bucket for the generated audio and HTML files, as well as the modified HTML file with updated image URLs
5. Verify that the modified HTML and audio files were successfully sent to the external API

## Conclusion

These two Lambda functions can be used together to automate the process of converting Docx files to HTML, generating audio from the HTML content, and calling an external API with the modified HTML and audio files. They can be customized and extended to meet the specific needs of your project.