"""
midio.codec.library — Local disc collection manager.

The library is where burned discs live on your machine.
It handles saving, loading, listing, and removing .disc files
from a local directory.

Think of it as your CD shelf.

Usage:
    from midio.codec import Library

    lib = Library()                     # ~/.midio/library/
    lib.save(disc)                      # saves morning_ritual.disc
    loaded = lib.load("morning_ritual") # loads it back
    lib.list()                          # ["morning_ritual", "email_triage"]
    lib.remove("morning_ritual")        # gone
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from .format import Disc


DEFAULT_LIBRARY_PATH = os.path.expanduser("~/.midio/library")
DISC_EXTENSION = ".disc"


class LibraryError(Exception):
    """Raised on library operations failure."""
    pass


class Library:
    """
    Local collection of .disc files.

    Each disc is stored as a JSON file with .disc extension.
    The library directory is created on first use.
    """

    def __init__(self, path: Optional[str] = None):
        self.path = Path(path or DEFAULT_LIBRARY_PATH)
        self.path.mkdir(parents=True, exist_ok=True)

    def _disc_path(self, name: str) -> Path:
        """Resolve path for a disc by name."""
        safe_name = name.replace("/", "_").replace("\\", "_")
        return self.path / f"{safe_name}{DISC_EXTENSION}"

    def save(self, disc: Disc, overwrite: bool = False) -> Path:
        """
        Save a disc to the library.

        Args:
            disc: The disc to save.
            overwrite: If False, raises if disc already exists.

        Returns:
            Path to the saved .disc file.
        """
        dest = self._disc_path(disc.metadata.name)
        if dest.exists() and not overwrite:
            raise LibraryError(
                f"Disc '{disc.metadata.name}' already exists. "
                f"Use overwrite=True to replace."
            )

        dest.write_text(disc.to_json(), encoding="utf-8")
        return dest

    def load(self, name: str) -> Disc:
        """
        Load a disc from the library by name.

        Args:
            name: Disc name (without .disc extension).

        Returns:
            The loaded Disc.

        Raises:
            LibraryError: If disc not found or corrupt.
        """
        path = self._disc_path(name)
        if not path.exists():
            raise LibraryError(f"Disc '{name}' not found in library")

        try:
            content = path.read_text(encoding="utf-8")
            return Disc.from_json(content)
        except (json.JSONDecodeError, KeyError) as e:
            raise LibraryError(f"Disc '{name}' is corrupt: {e}")

    def load_from_file(self, file_path: str) -> Disc:
        """Load a disc from an arbitrary file path."""
        path = Path(file_path)
        if not path.exists():
            raise LibraryError(f"File not found: {file_path}")
        content = path.read_text(encoding="utf-8")
        return Disc.from_json(content)

    def list(self) -> List[str]:
        """List all disc names in the library."""
        return sorted(
            p.stem for p in self.path.glob(f"*{DISC_EXTENSION}")
        )

    def list_detailed(self) -> List[Dict]:
        """List all discs with metadata."""
        details = []
        for name in self.list():
            try:
                disc = self.load(name)
                details.append({
                    "name": disc.metadata.name,
                    "version": disc.metadata.version,
                    "author": disc.metadata.author,
                    "tracks": len(disc.tracks),
                    "auth_required": [a.toolkit for a in disc.auth_manifest],
                    "checksum": disc.checksum,
                })
            except LibraryError:
                details.append({"name": name, "error": "corrupt"})
        return details

    def remove(self, name: str) -> bool:
        """Remove a disc from the library. Returns True if removed."""
        path = self._disc_path(name)
        if path.exists():
            path.unlink()
            return True
        return False

    def has(self, name: str) -> bool:
        """Check if a disc exists in the library."""
        return self._disc_path(name).exists()

    def import_disc(self, file_path: str, overwrite: bool = False) -> Disc:
        """Import a .disc file from anywhere into the library."""
        disc = self.load_from_file(file_path)
        self.save(disc, overwrite=overwrite)
        return disc

    def export_disc(self, name: str, dest_path: str) -> Path:
        """Export a disc from the library to a file."""
        disc = self.load(name)
        dest = Path(dest_path)
        dest.write_text(disc.to_json(), encoding="utf-8")
        return dest

    def __len__(self):
        return len(self.list())

    def __repr__(self):
        return f"<Library path=\'{self.path}\' discs={len(self)}>"
