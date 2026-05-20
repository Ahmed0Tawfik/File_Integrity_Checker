"""
hasher.py — Core hash engine.
Reads files in 64 KB chunks to handle large files without memory issues.
"""

import hashlib
import os
from typing import Tuple

CHUNK_SIZE = 65536  # 64 KB


def hash_file(filepath: str, algorithm: str = "sha256") -> str:
    """
    Reads a file in binary chunks and returns its hex digest.

    Args:
        filepath: Absolute or relative path to the file.
        algorithm: Any hashlib-supported algorithm (sha256, sha512, md5, sha1, etc.)

    Returns:
        Lowercase hex digest string.

    Raises:
        ValueError: If the algorithm is not supported.
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.
    """
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
    """
    Directly compares two files by hash without any baseline.

    Args:
        file1: Path to the first file.
        file2: Path to the second file.
        algorithm: Hash algorithm to use.

    Returns:
        Tuple of (are_identical: bool, hash1: str, hash2: str)
    """
    h1 = hash_file(file1, algorithm)
    h2 = hash_file(file2, algorithm)
    return h1 == h2, h1, h2


def get_supported_algorithms() -> list:
    """Returns a sorted list of commonly useful hash algorithms."""
    preferred = ["sha256", "sha512", "sha3_256", "sha3_512", "sha1", "md5", "blake2b", "blake2s"]
    available = hashlib.algorithms_available
    return [a for a in preferred if a in available]


def avalanche_demo(text1: str, text2: str, algorithm: str = "sha256") -> dict:
    """
    Hashes two strings and computes bit-level difference to demonstrate the avalanche effect.

    Args:
        text1: First input string.
        text2: Second input string (ideally differing by one character).
        algorithm: Hash algorithm to use.

    Returns:
        dict with hash1, hash2, hex_diff_count, bit_diff_count, bit_diff_percent
    """
    h = hashlib.new(algorithm)
    h.update(text1.encode("utf-8"))
    hash1_hex = h.hexdigest()

    h2 = hashlib.new(algorithm)
    h2.update(text2.encode("utf-8"))
    hash2_hex = h2.hexdigest()

    # Convert hex to bytes and count differing bits
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
