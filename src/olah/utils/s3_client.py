# coding=utf-8
# Copyright 2024 XiaHan
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import datetime
import hashlib
import hmac
import os
from typing import AsyncIterator, Dict

import aiofiles
import httpx
from urllib.parse import urlparse


class S3Client:
    """Minimal S3 client using httpx and SigV4 signing."""

    def __init__(
        self,
        endpoint: str,
        region: str,
        access_key: str,
        secret_key: str,
        bucket: str,
    ) -> None:
        self._endpoint = endpoint.rstrip("/")
        self._region = region
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket

    @property
    def bucket(self) -> str:
        return self._bucket

    def _sign(self, key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _signature_key(self, date_stamp: str) -> bytes:
        k_date = self._sign(("AWS4" + self._secret_key).encode("utf-8"), date_stamp)
        k_region = self._sign(k_date, self._region)
        k_service = self._sign(k_region, "s3")
        k_signing = self._sign(k_service, "aws4_request")
        return k_signing

    def _build_auth_headers(
        self,
        method: str,
        canonical_uri: str,
        canonical_querystring: str,
        headers: Dict[str, str],
        payload_hash: str,
    ) -> Dict[str, str]:
        time_now = datetime.datetime.utcnow()
        amz_date = time_now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = time_now.strftime("%Y%m%d")

        signed_headers_list = sorted([h.lower() for h in headers.keys()])
        canonical_headers = "".join([f"{h}:{headers[h]}\n" for h in signed_headers_list])
        signed_headers = ";".join(signed_headers_list)

        canonical_request = "\n".join(
            [
                method,
                canonical_uri,
                canonical_querystring,
                canonical_headers,
                signed_headers,
                payload_hash,
            ]
        )

        credential_scope = f"{date_stamp}/{self._region}/s3/aws4_request"
        string_to_sign = "\n".join(
            [
                "AWS4-HMAC-SHA256",
                amz_date,
                credential_scope,
                hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
            ]
        )

        signing_key = self._signature_key(date_stamp)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization_header = (
            f"AWS4-HMAC-SHA256 Credential={self._access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, Signature={signature}"
        )

        signed = {
            "Authorization": authorization_header,
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload_hash,
        }
        signed.update(headers)
        return signed

    async def _file_body(self, path: str) -> AsyncIterator[bytes]:
        async with aiofiles.open(path, "rb") as f:
            while True:
                chunk = await f.read(1024 * 1024)
                if not chunk:
                    break
                yield chunk

    async def upload_file(self, key: str, file_path: str) -> None:
        """Upload a single file to the configured bucket using streaming."""

        object_key = key.lstrip("/")
        url = f"{self._endpoint}/{self._bucket}/{object_key}"
        parsed = urlparse(url)
        headers = {
            "host": parsed.netloc,
            "content-length": str(os.path.getsize(file_path)),
        }
        payload_hash = "UNSIGNED-PAYLOAD"
        signed_headers = self._build_auth_headers(
            method="PUT",
            canonical_uri=parsed.path,
            canonical_querystring=parsed.query,
            headers=headers,
            payload_hash=payload_hash,
        )

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "PUT", url, headers=signed_headers, content=self._file_body(file_path)
            ) as response:
                await response.aread()
                response.raise_for_status()
