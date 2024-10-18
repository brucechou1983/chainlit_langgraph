import boto3
import hashlib
import uuid
from typing import Any, Dict, Union
from chainlit.logger import logger
from chainlit.data.base import BaseStorageClient
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship


class MinIOStorageClient(BaseStorageClient):
    """
    Class to enable MinIO storage provider using the S3 compatible API
    """

    def __init__(self, bucket: str, endpoint_url: str, access_key: str, secret_key: str):
        try:
            self.bucket = bucket
            # Initialize boto3 client with MinIO-specific configurations
            self.client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
            )
            logger.info("MinIOStorageClient initialized")
        except Exception as e:
            logger.warning(f"MinIOStorageClient initialization error: {e}")

    async def upload_file(
        self,
        object_key: str,
        data: Union[bytes, str],
        mime: str = "application/octet-stream",
        overwrite: bool = True,
        content_md5: bool = False  # Optionally send content-md5
    ) -> Dict[str, Any]:
        try:
            # Optionally calculate and send content-md5
            extra_args = {"ContentType": mime}
            if content_md5:
                md5_hash = hashlib.md5(data if isinstance(
                    data, bytes) else data.encode('utf-8')).digest()
                extra_args["ContentMD5"] = md5_hash

            self.client.put_object(
                Bucket=self.bucket, Key=object_key, Body=data, **extra_args
            )
            url = f"{self.client.meta.endpoint_url}/{self.bucket}/{object_key}"
            return {"object_key": object_key, "url": url}
        except Exception as e:
            logger.warning(f"MinIOStorageClient, upload_file error: {e}")
            return {}


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    identifier = Column(String, nullable=False, unique=True)
    metadata_ = Column("metadata", JSONB, nullable=False)
    createdAt = Column(String)


class Thread(Base):
    __tablename__ = 'threads'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    createdAt = Column(String)
    name = Column(String)
    userId = Column(PG_UUID(as_uuid=True), ForeignKey(
        'users.id', ondelete='CASCADE'))
    userIdentifier = Column(String)
    tags = Column(ARRAY(String))
    metadata_ = Column("metadata", JSONB)

    user = relationship("User", backref="threads")


class Step(Base):
    __tablename__ = 'steps'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    threadId = Column(PG_UUID(as_uuid=True), ForeignKey(
        'threads.id'), nullable=False)
    parentId = Column(PG_UUID(as_uuid=True))
    disableFeedback = Column(Boolean, nullable=True)
    streaming = Column(Boolean, nullable=False)
    waitForAnswer = Column(Boolean)
    isError = Column(Boolean)
    metadata_ = Column("metadata", JSONB)
    tags = Column(ARRAY(String))
    input = Column(Text)
    output = Column(Text)
    createdAt = Column(String)
    start = Column(String)
    end = Column(String)
    generation = Column(JSONB)
    showInput = Column(Text)
    language = Column(String)
    indent = Column(Integer)


class Element(Base):
    __tablename__ = 'elements'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    threadId = Column(PG_UUID(as_uuid=True), ForeignKey('threads.id'))
    type = Column(String)
    url = Column(String)
    chainlitKey = Column(String)
    name = Column(String, nullable=False)
    display = Column(String)
    objectKey = Column(String)
    size = Column(String)
    page = Column(Integer)
    language = Column(String)
    forId = Column(PG_UUID(as_uuid=True))
    mime = Column(String)


class Feedback(Base):
    __tablename__ = 'feedbacks'
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forId = Column(PG_UUID(as_uuid=True), nullable=False)
    threadId = Column(PG_UUID(as_uuid=True), ForeignKey(
        'threads.id'), nullable=False)
    value = Column(Integer, nullable=False)
    comment = Column(Text)

    thread = relationship("Thread", backref="feedbacks")
