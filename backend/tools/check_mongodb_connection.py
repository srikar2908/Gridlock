import asyncio
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

sys.path.append(str(Path(__file__).resolve().parents[1]))

from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402
from app.core.config import get_settings  # noqa: E402


def sanitize_uri(uri: str) -> str:
    return re.sub(r"mongodb(\+srv)?://<([^>]+)>:", r"mongodb\1://\2:", uri)


def safe_host(uri: str) -> str:
    sanitized = re.sub(r"(mongodb(?:\+srv)?://)([^:@]+):([^@]+)@", r"\1", uri)
    return urlsplit(sanitized).netloc


async def main() -> int:
    settings = get_settings()
    uri = sanitize_uri(settings.mongodb_uri)
    print(f"configured={bool(uri)}")
    print(f"host={safe_host(uri) if uri else None}")
    print(f"database={settings.database_name}")
    if not uri:
        print("error=MONGODB_URI is missing")
        return 1
    client = None
    try:
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=8000)
        await client.admin.command("ping")
        print("connected=true")
        print("diagnostics=MongoDB ping succeeded. Credentials, network access, and TLS are usable from this machine.")
        return 0
    except Exception as exc:
        print("connected=false")
        print(f"error={exc}")
        print("check=Verify username/password, Atlas Network Access IP allowlist, database user permissions, and TLS/SSL interception.")
        return 2
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
