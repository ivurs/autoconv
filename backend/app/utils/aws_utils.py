import os
from io import BytesIO
from fastapi import UploadFile
import datetime
from termcolor import colored

import boto3
from dotenv import load_dotenv

load_dotenv()  # 加载项目根目录下的 .env 文件

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BUCKET_NAME = os.getenv("BUCKET_NAME")
print(F"BUCKET_NAME: {BUCKET_NAME}")


def upload_to_aws(file: UploadFile, file_name: str) -> str:
    """
    上传文件到AWS
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="ap-southeast-2"
    )

    response = s3.get_bucket_location(Bucket=BUCKET_NAME)
    print(response["LocationConstraint"])

    bucket_name = BUCKET_NAME

    # Create the bucket if it doesn't exist
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"}
        )
        print(f"✅ Created bucket: {bucket_name}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"ℹ️ Bucket already exists: {bucket_name}")

     # 构建S3存储路径
    s3_key = f"uploads/{file_name}"

    # 获取文件内容类型
    content_type = file.content_type
    print(f"文件类型: {content_type}")

    # 获取原始文件名
    original_filename = file.filename
    print(f"原始文件名: {original_filename}")

  
    # 读取文件内容
    file_content = file.file.read()

     # 上传到S3
    try:
        s3.put_object(
            Bucket=bucket_name,        # 存储桶：'my-app-files'
            Key=s3_key,                     # S3路径：'user-uploads/photo.jpg'
            Body=file_content,                  # 文件内容：图片的二进制数据
            ContentType=file.content_type,  # 内容类型：'image/jpeg'
            Metadata={
                'original-filename': file_name  # 元数据：保存原始文件名'photo.jpg'
            }
        )
        print(f"✅ Uploaded {original_filename} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

    #print(datetime.datetime.now())
    print(colored(datetime.datetime.now(), "red"))
    ## 生成预签名URL（可选，用于直接访问）不是永久的，这个逻辑和阿里云的逻辑不一样，这个地方还要重新设计
    presigned_url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucket_name, 'Key': s3_key},
    ExpiresIn=604800  # 7天 = 60*60*24*7
    )
    print(f"presigned_url ： {presigned_url}")
    # 将文件信息保存到数据库

    file_url = presigned_url
   
    # 创建 OSS 客户端
    #auth = oss2.Auth(OSS_ACCESS_KEY, OSS_SECRET_KEY)
    #bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)

    # 读取文件内容
    #file_content = file.file.read()

    # 上传到 OSS
    #bucket.put_object(file_name, file_content)

    # 文件 URL（根据你的 OSS 配置，这里可能需要调整）
    #file_url = f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}/{file_name}"

    return file_url


def upload_local_to_aws(local_file: str,file_name: str) -> str:
    """
    上传文件到AWS
    """
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name="ap-southeast-2"
    )

    response = s3.get_bucket_location(Bucket=BUCKET_NAME)
    print(response["LocationConstraint"])

    bucket_name = BUCKET_NAME

    # Create the bucket if it doesn't exist
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"}
        )
        print(f"✅ Created bucket: {bucket_name}")
    except s3.exceptions.BucketAlreadyOwnedByYou:
        print(f"ℹ️ Bucket already exists: {bucket_name}")

     # 构建S3存储路径
    s3_key = f"uploads/{file_name}"

    # Upload
    try:
        s3.upload_file(local_file, bucket_name, s3_key)
        print(f"✅ Uploaded {local_file} to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

    #print(datetime.datetime.now())
    print(colored(datetime.datetime.now(), "red"))
    ## 生成预签名URL（可选，用于直接访问）不是永久的，这个逻辑和阿里云的逻辑不一样，这个地方还要重新设计
    presigned_url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucket_name, 'Key': s3_key},
    ExpiresIn=604800  # 7天 = 60*60*24*7
    )
    print(f"presigned_url ： {presigned_url}")
    # 将文件信息保存到数据库

    file_url = presigned_url


    return file_url