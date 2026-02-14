"""
Tests for midio.codec — the disc encoding/decoding system.
"""

import json
import tempfile
import os
import pytest
from src.canvas.node import Node, NodeType, YarnType
from src.loom.runtime import Loom
from src.codec.format import Disc, DiscMetadata, Track, AuthRequirement, DISC_FORMAT_VERSION
from src.codec.encoder import Encoder
from src.codec.decoder import Decoder, DecoderError
from src.codec.library import Library, LibraryError


# ---- Fixtures ----

def make_email_loom():
    """Build a simple email processing loom for testing."""
    loom = Loom(name="email_test")

    fetch = Node(name="fetch_emails", node_type=NodeType.SOURCE)
    summarize = Node(name="summarize", node_type=NodeType.TRANSFORM)
    notify = Node(name="notify", node_type=NodeType.ACTION)

    loom.add_node(fetch)
    loom.add_node(summarize)
    loom.add_node(notify)

    fetch.connect(summarize)
    summarize.connect(notify)

    return loom, fetch, summarize, notify


# ---- Format tests ----

class TestDiscFormat:
    def test_create_disc(self):
        meta = DiscMetadata(name="test_disc", author="yael")
        disc = Disc(metadata=meta)
        assert disc.metadata.name == "test_disc"
        assert disc.format_version == DISC_FORMAT_VERSION

    def test_add_tracks(self):
        meta = DiscMetadata(name="test")
        track = Track(name="fetch", node_type="source", handler="GMAIL_FETCH_EMAILS")
        disc = Disc(metadata=meta, tracks=[track])
        assert len(disc.tracks) == 1
        assert disc.tracks[0].handler == "GMAIL_FETCH_EMAILS"

    def test_auth_manifest_deduplication(self):
        auth = AuthRequirement(toolkit="gmail", reason="fetch")
        t1 = Track(name="t1", node_type="source", auth=[auth])
        t2 = Track(name="t2", node_type="source", auth=[auth])
        disc = Disc(metadata=DiscMetadata(name="test"), tracks=[t1, t2])
        assert len(disc.auth_manifest) == 1

    def test_topology_computed(self):
        t1 = Track(name="fetch", node_type="source", outputs_to=["process"])
        t2 = Track(name="process", node_type="transform")
        disc = Disc(metadata=DiscMetadata(name="test"), tracks=[t1, t2])
        assert disc.topology == {"fetch": ["process"], "process": []}

    def test_checksum_deterministic(self):
        meta = DiscMetadata(name="test", created_at="2026-01-01T00:00:00+00:00")
        t = Track(name="a", node_type="source")
        d1 = Disc(metadata=meta, tracks=[t])
        d2 = Disc(metadata=meta, tracks=[t])
        assert d1.checksum == d2.checksum

    def test_json_roundtrip(self):
        meta = DiscMetadata(name="roundtrip", author="test")
        track = Track(
            name="fetch",
            node_type="source",
            handler="GMAIL_FETCH_EMAILS",
            handler_type="composio",
            auth=[AuthRequirement(toolkit="gmail")],
            outputs_to=["process"],
        )
        track2 = Track(name="process", node_type="transform", inputs_from=["fetch"])
        disc = Disc(metadata=meta, tracks=[track, track2])

        json_str = disc.to_json()
        loaded = Disc.from_json(json_str)

        assert loaded.metadata.name == "roundtrip"
        assert len(loaded.tracks) == 2
        assert loaded.tracks[0].handler == "GMAIL_FETCH_EMAILS"
        assert loaded.topology == {"fetch": ["process"], "process": []}

    def test_validate_good_disc(self):
        t1 = Track(name="a", node_type="source", outputs_to=["b"])
        t2 = Track(name="b", node_type="transform", inputs_from=["a"])
        disc = Disc(metadata=DiscMetadata(name="valid"), tracks=[t1, t2])
        assert disc.validate() == []

    def test_validate_missing_reference(self):
        t1 = Track(name="a", node_type="source", outputs_to=["nonexistent"])
        disc = Disc(metadata=DiscMetadata(name="bad"), tracks=[t1])
        issues = disc.validate()
        assert any("nonexistent" in issue for issue in issues)

    def test_validate_no_tracks(self):
        disc = Disc(metadata=DiscMetadata(name="empty"))
        assert any("no tracks" in issue for issue in disc.validate())


# ---- Encoder tests ----

class TestEncoder:
    def test_burn_loom(self):
        loom, fetch, summarize, notify = make_email_loom()
        disc = Encoder.burn(loom, name="email_workflow", author="yael")

        assert disc.metadata.name == "email_workflow"
        assert len(disc.tracks) == 3
        track_names = [t.name for t in disc.tracks]
        assert "fetch_emails" in track_names
        assert "summarize" in track_names
        assert "notify" in track_names

    def test_burn_preserves_wiring(self):
        loom, fetch, summarize, notify = make_email_loom()
        disc = Encoder.burn(loom, name="wiring_test")

        fetch_track = next(t for t in disc.tracks if t.name == "fetch_emails")
        assert "summarize" in fetch_track.outputs_to

        summarize_track = next(t for t in disc.tracks if t.name == "summarize")
        assert "fetch_emails" in summarize_track.inputs_from
        assert "notify" in summarize_track.outputs_to

    def test_burn_with_skill_map(self):
        loom, fetch, summarize, notify = make_email_loom()
        skill_map = {
            fetch.id: {
                "tool_slug": "GMAIL_FETCH_EMAILS",
                "handler_type": "composio",
            }
        }
        disc = Encoder.burn(loom, name="skilled", skill_map=skill_map)
        fetch_track = next(t for t in disc.tracks if t.name == "fetch_emails")
        assert fetch_track.handler == "GMAIL_FETCH_EMAILS"
        assert len(fetch_track.auth) == 1
        assert fetch_track.auth[0].toolkit == "gmail"

    def test_burn_single_track(self):
        node = Node(name="test_node", node_type=NodeType.ACTION)
        track = Encoder.burn_track(node, tool_slug="SLACK_SEND_MESSAGE")
        assert track.name == "test_node"
        assert track.handler == "SLACK_SEND_MESSAGE"
        assert track.auth[0].toolkit == "slack"


# ---- Decoder tests ----

class TestDecoder:
    def test_load_disc_to_loom(self):
        loom, *_ = make_email_loom()
        disc = Encoder.burn(loom, name="decode_test")
        loaded_loom = Decoder.load(disc)

        assert loaded_loom.name == "decode_test"
        assert len(loaded_loom.nodes) == 3

    def test_roundtrip_loom_disc_loom(self):
        """Encode a loom, decode it, verify topology matches."""
        original, *_ = make_email_loom()
        disc = Encoder.burn(original, name="roundtrip")
        restored = Decoder.load(disc)

        original_topo = original.get_topology()
        restored_topo = restored.get_topology()

        # Compare by node names (IDs will differ)
        def topo_by_name(loom_instance):
            id_to_name = {nid: n.name for nid, n in loom_instance.nodes.items()}
            return {
                id_to_name[nid]: sorted(id_to_name[t] for t in targets)
                for nid, targets in loom_instance.get_topology().items()
            }

        assert topo_by_name(original) == topo_by_name(restored)

    def test_strict_mode_rejects_bad_disc(self):
        bad_track = Track(name="broken", node_type="source", outputs_to=["ghost"])
        disc = Disc(metadata=DiscMetadata(name="bad"), tracks=[bad_track])
        with pytest.raises(DecoderError):
            Decoder.load(disc, strict=True)

    def test_preview(self):
        loom, *_ = make_email_loom()
        disc = Encoder.burn(loom, name="preview_test", author="yael")
        preview = Decoder.preview(disc)
        assert "preview_test" in preview
        assert "yael" in preview
        assert "fetch_emails" in preview


# ---- Library tests ----

class TestLibrary:
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lib = Library(path=tmpdir)
            loom, *_ = make_email_loom()
            disc = Encoder.burn(loom, name="saved_disc")

            lib.save(disc)
            loaded = lib.load("saved_disc")

            assert loaded.metadata.name == "saved_disc"
            assert len(loaded.tracks) == 3

    def test_list_discs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lib = Library(path=tmpdir)
            for name in ["alpha", "beta", "gamma"]:
                meta = DiscMetadata(name=name)
                lib.save(Disc(metadata=meta, tracks=[Track(name="t", node_type="source")]))

            names = lib.list()
            assert names == ["alpha", "beta", "gamma"]

    def test_remove_disc(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lib = Library(path=tmpdir)
            meta = DiscMetadata(name="removable")
            lib.save(Disc(metadata=meta, tracks=[Track(name="t", node_type="source")]))
            assert lib.has("removable")
            lib.remove("removable")
            assert not lib.has("removable")

    def test_no_overwrite_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lib = Library(path=tmpdir)
            meta = DiscMetadata(name="protected")
            disc = Disc(metadata=meta, tracks=[Track(name="t", node_type="source")])
            lib.save(disc)
            with pytest.raises(LibraryError):
                lib.save(disc)

    def test_overwrite_when_allowed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lib = Library(path=tmpdir)
            meta = DiscMetadata(name="updatable")
            disc = Disc(metadata=meta, tracks=[Track(name="t", node_type="source")])
            lib.save(disc)
            lib.save(disc, overwrite=True)  # should not raise
            assert lib.has("updatable")

    def test_export_import(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lib = Library(path=os.path.join(tmpdir, "lib"))
            meta = DiscMetadata(name="portable")
            disc = Disc(metadata=meta, tracks=[Track(name="t", node_type="source")])
            lib.save(disc)

            export_path = os.path.join(tmpdir, "portable.disc")
            lib.export_disc("portable", export_path)

            lib2 = Library(path=os.path.join(tmpdir, "lib2"))
            imported = lib2.import_disc(export_path)
            assert imported.metadata.name == "portable"
            assert lib2.has("portable")
