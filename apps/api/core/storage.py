from abc import ABC, abstractmethod
import os
import asyncio
import aiofiles
from core.config import settings

class StorageBackend(ABC):
    @abstractmethod
    async def save(self, key: str, content: bytes | str) -> str: ...
    @abstractmethod
    async def get(self, key: str) -> bytes: ...
    @abstractmethod
    async def delete(self, key: str) -> None: ...
    @abstractmethod
    async def get_signed_url(self, key: str, expiry_seconds: int = 3600) -> str: ...

class LocalStorageBackend(StorageBackend):
    def __init__(self):
        self.base_path = settings.LOCAL_STORAGE_PATH
        os.makedirs(self.base_path, exist_ok=True)
        
    async def save(self, key: str, content: bytes | str) -> str:
        path = os.path.join(self.base_path, key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        mode = 'wb' if isinstance(content, bytes) else 'w'
        async with aiofiles.open(path, mode) as f:
            await f.write(content)
        return key

    async def get(self, key: str) -> bytes:
        path = os.path.join(self.base_path, key)
        async with aiofiles.open(path, 'rb') as f:
            return await f.read()

    async def delete(self, key: str) -> None:
        path = os.path.join(self.base_path, key)
        if os.path.exists(path):
            os.remove(path)

    async def get_signed_url(self, key: str, expiry_seconds: int = 3600) -> str:
        return f"/api/v1/storage/{key}"

class S3StorageBackend(StorageBackend):
    def __init__(self):
        import boto3
        from botocore.config import Config

        session = boto3.session.Session()
        client_kwargs = {
            'service_name': 's3',
            'config': Config(signature_version='s3v4'),
        }
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            client_kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID
            client_kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY
        if settings.S3_ENDPOINT:
            client_kwargs['endpoint_url'] = settings.S3_ENDPOINT

        self.s3_client = session.client(**client_kwargs)
        self.bucket = settings.S3_BUCKET

    async def save(self, key: str, content: bytes | str) -> str:
        body = content.encode('utf-8') if isinstance(content, str) else content

        def _put():
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=body,
            )

        await asyncio.to_thread(_put)
        return key

    async def get(self, key: str) -> bytes:
        def _get():
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()

        return await asyncio.to_thread(_get)

    async def delete(self, key: str) -> None:
        def _del():
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)

        await asyncio.to_thread(_del)

    async def get_signed_url(self, key: str, expiry_seconds: int = 3600) -> str:
        def _gen_url():
            return self.s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expiry_seconds,
            )

        return await asyncio.to_thread(_gen_url)

def get_storage() -> StorageBackend:
    if settings.STORAGE_BACKEND == 's3':
        return S3StorageBackend()
    return LocalStorageBackend()
