import hashlib
import os
from typing import Tuple

CHUNK_SIZE = 65536


def hash_file(filepath: str, algorithm: str = "sha256") -> str:
    try:
        h = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"Unsupported hash algorithm: '{algorithm}'. "
                         f"Supported: {', '.join(sorted(hashlib.algorithms_available))}")

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            h.update(chunk)

    return h.hexdigest()


def compare_files(file1: str, file2: str, algorithm: str = "sha256") -> Tuple[bool, str, str]:
    h1 = hash_file(file1, algorithm)
    h2 = hash_file(file2, algorithm)
    return h1 == h2, h1, h2


def get_supported_algorithms() -> list:
    preferred = ["sha256", "sha512", "sha3_256", "sha3_512", "sha1", "md5", "blake2b", "blake2s"]
    available = hashlib.algorithms_available
    return [a for a in preferred if a in available]


def avalanche_demo(text1: str, text2: str, algorithm: str = "sha256") -> dict:
    h = hashlib.new(algorithm)
    h.update(text1.encode("utf-8"))
    hash1_hex = h.hexdigest()

    h2 = hashlib.new(algorithm)
    h2.update(text2.encode("utf-8"))
    hash2_hex = h2.hexdigest()

    bytes1 = bytes.fromhex(hash1_hex)
    bytes2 = bytes.fromhex(hash2_hex)

    total_bits = len(bytes1) * 8
    diff_bits = sum(bin(b1 ^ b2).count("1") for b1, b2 in zip(bytes1, bytes2))
    diff_hex_chars = sum(1 for c1, c2 in zip(hash1_hex, hash2_hex) if c1 != c2)

    return {
        "hash1": hash1_hex,
        "hash2": hash2_hex,
        "hex_diff_count": diff_hex_chars,
        "total_hex_chars": len(hash1_hex),
        "bit_diff_count": diff_bits,
        "total_bits": total_bits,
        "bit_diff_percent": round(diff_bits / total_bits * 100, 1),
    }
