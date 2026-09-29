"""Minimal HS256 JSON Web Tokens (stdlib only).

Each simulated issuer (Entra ID, IBM Verify, the sandbox's workload attestor)
signs with its own key, so a token from one issuer can never pass as another's.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time


class InvalidToken(Exception):
    pass


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _b64d(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def sign(claims: dict, key: bytes, kid: str) -> str:
    header = {"alg": "HS256", "typ": "JWT", "kid": kid}
    head = _b64e(json.dumps(header, separators=(",", ":")).encode())
    body = _b64e(json.dumps(claims, separators=(",", ":"), ensure_ascii=False).encode())
    sig = hmac.new(key, f"{head}.{body}".encode(), hashlib.sha256).digest()
    return f"{head}.{body}.{_b64e(sig)}"


def decode(token: str) -> dict:
    """Read claims WITHOUT checking the signature (display only)."""
    try:
        return json.loads(_b64d(token.split(".")[1]))
    except Exception as exc:  # noqa: BLE001
        raise InvalidToken("jeton illisible") from exc


def verify(token: str, keys: dict[str, bytes], now: float | None = None) -> dict:
    """Check signature against the issuer keys we trust, then expiry."""
    try:
        head_b64, body_b64, sig_b64 = token.split(".")
        header = json.loads(_b64d(head_b64))
    except Exception as exc:  # noqa: BLE001
        raise InvalidToken("jeton mal formé") from exc
    key = keys.get(header.get("kid", ""))
    if key is None or header.get("alg") != "HS256":
        raise InvalidToken("émetteur non reconnu")
    expected = hmac.new(key, f"{head_b64}.{body_b64}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, _b64d(sig_b64)):
        raise InvalidToken("signature invalide")
    claims = json.loads(_b64d(body_b64))
    if claims.get("exp", 0) < (now or time.time()):
        raise InvalidToken("jeton expiré")
    return claims
