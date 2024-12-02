import base64
import zlib
from base64 import decode, urlsafe_b64decode

def decode_level(level_data: str, is_official_level = False) -> str:
    if is_official_level:
        level_data = 'H4sIAAAAAAAAA' + level_data
    base64_decoded = base64.urlsafe_b64decode(level_data.encode())

    decompressed = zlib.decompress(base64_decoded, 15 | 32)
    return decompressed.decode()
