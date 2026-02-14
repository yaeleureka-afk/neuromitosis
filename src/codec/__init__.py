"""
midio.codec — Encode, decode, and share skill libraries.

The codec is Midio's serialization layer. It captures node graphs,
loom topologies, molt invariants, and skill requirements into portable
disc files that can be shared, versioned, and loaded into any Midio runtime.

Think of it as FFmpeg for agent skills:
  - Encoder: canvas → .disc file
  - Decoder: .disc file → runnable graph
  - Library: local collection of installed discs

💿 LLM CDs — the CLI reinvented for the MCP era.
"""

from .format import Disc, Track, AuthRequirement, DiscMetadata
from .encoder import Encoder
from .decoder import Decoder
from .library import Library

__all__ = [
    "Disc",
    "Track",
    "AuthRequirement",
    "DiscMetadata",
    "Encoder",
    "Decoder",
    "Library",
]
