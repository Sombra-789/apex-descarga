"""Pruebas unitarias autocontenidas; no requieren acceso a Internet."""
from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from apex_desktop.coordinator import DownloadCoordinator
from apex_desktop.engine import JobCancelled, MediaEngine, extract_metadata, format_expression
from apex_desktop.models import DownloadJob, QUALITIES, THEMES, display_bytes, display_duration, is_hex_color, validate_url
from apex_desktop.storage import AppStore, atomic_json, load_json, MAX_HISTORY


class ValidationTests(unittest.TestCase):
    def test_supported_urls(self):
        for x in ("https://youtu.be/abc", "https://www.youtube.com/watch?v=xyz", "http://example.com/abc", "https://example.com:443/v"):
            self.assertEqual(validate_url(x), x)

    def test_bad_urls(self):
        bad = ["", " ", "ftp://example.com", "file:///etc/passwd", "https://localhost/x",
               "http://127.0.0.1:8000/a", "http://192.168.1.1", "http://10.0.0.1",
               "http://[::1]/", "https://host.local/a", "http://u:pass@example.com",
               "https://example.com:abc", "http:///abc", "https://example.com/" + "x"*4100]
        for x in bad:
            with self.subTest(x=x):
                with self.assertRaises(ValueError):
                    validate_url(x)

    def test_hex(self):
        self.assertTrue(is_hex_color("#aBc123"))
        for x in ("123456", "#1234", "#gggggg", "#1234567", "#f1f1f\n"):
            self.assertFalse(is_hex_color(x))

    def test_duration(self):
        self.assertEqual(display_duration(0), "0:00")
        self.assertEqual(display_duration(185), "3:05")
        self.assertEqual(display_duration(3601), "1:00:01")
        self.assertEqual(display_duration(None), "—")

    def test_bytes(self):
        self.assertEqual(display_bytes(0), "0 B")
        self.assertEqual(display_bytes(1024), "1.0 KB")
        self.assertEqual(display_bytes(None), "—")

    def test_job_validation(self):
        j = DownloadJob("https://example.com/a")
        self.assertEqual(j.state, "pendiente")
        self.assertEqual(j.quality, "1080p")
        self.assertIn(j.quality, QUALITIES)
        with self.assertRaises(ValueError): DownloadJob("http://localhost",kind="video")
        with self.assertRaises(ValueError): DownloadJob("https://example.com",kind="zip")
        with self.assertRaises(ValueError): DownloadJob("https://example.com",quality="8K")

    def test_job_roundtrip(self):
        j = DownloadJob("https://example.com",title="Música",kind="audio",quality="Mejor disponible")
        self.assertEqual(DownloadJob.from_dict(j.to_dict()).to_dict(),j.to_dict())
        data=j.to_dict();data["new_option"]=3
        self.assertEqual(DownloadJob.from_dict(data).title,j.title)

    def test_preserves_accent_values(self):
        for name,color in THEMES.items():
            self.assertTrue(is_hex_color(color),name)


class EngineTests(unittest.TestCase):
    def test_format_choices(self):
        fmt = format_expression("video","720p",True)
        self.assertIn("height<=720",fmt)
        self.assertIn("+ba",fmt)
        self.assertNotIn("+ba",format_expression("video","1080p",False))
        self.assertNotIn("height<=",format_expression("video","Mejor disponible",True))
        self.assertEqual(format_expression("audio","1080p",True),"bestaudio/best")

    def test_extract(self):
        x = extract_metadata({"title":"Canción", "uploader":"Canal", "duration":205.7, "thumbnail":"https://example.com/pic.jpg", "id":"123"})
        self.assertEqual(x["title"],"Canción")
        self.assertEqual(x["duration"],205)
        self.assertEqual(x["id"],"123")

    def test_fallback_thumbnail(self):
        x = extract_metadata({"title":"Test", "thumbnails":[{"url":"https://example.com/1.png"},{"url":"https://example.com/2.jpg"}]})
        self.assertEqual(x["thumbnail"],"https://example.com/2.jpg")
        self.assertEqual(x["uploader"],"")
        self.assertIsNone(x["duration"])

    def test_no_unsafe_metadata_headers(self):
        x = extract_metadata({"title":"ok", "cookies":"SECRET", "http_headers":{"Authorization":"Bearer secret"}})
        self.assertNotIn("cookies",x)
        self.assertNotIn("http_headers",x)

    def test_file_detection(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/"Song [xyz].mp3"
            p.write_bytes(b"sound")
            got=MediaEngine._find_file({"id":"xyz"},Path(d)/"Song [xyz].webm",Path(d),"audio")
            self.assertEqual(got,p)


class StorageTests(unittest.TestCase):
    def test_atomic_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"inner"/"test.json"
            atomic_json(path,{"hola":"mundo"})
            self.assertEqual(load_json(path,{}),{"hola":"mundo"})
            self.assertFalse(path.with_suffix(".json.tmp").exists())

    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"test.json"
            path.write_text("invalid",encoding="utf-8")
            self.assertEqual(load_json(path,[1]),[1])

    def test_new_store(self):
        with tempfile.TemporaryDirectory() as d:
            store=AppStore(Path(d))
            self.assertEqual(store.jobs,[])
            self.assertEqual(store.settings["theme"],"Violeta")
            self.assertFalse(store.settings["compact_mode"])

    def test_persistence(self):
        with tempfile.TemporaryDirectory() as d:
            store=AppStore(Path(d))
            store.add_job(DownloadJob("https://example.com/abc",title="Guardado"))
            store.settings["theme"]="Coral"
            store.settings["compact_mode"]=True
            store.save_settings()
            loaded=AppStore(Path(d))
            self.assertEqual(loaded.settings["theme"],"Coral")
            self.assertTrue(loaded.settings["compact_mode"])
            self.assertEqual(loaded.jobs[0].title,"Guardado")
            self.assertEqual(loaded.jobs[0].state,"interrumpido")

    def test_limit(self):
        with tempfile.TemporaryDirectory() as d:
            store=AppStore(Path(d))
            for n in range(MAX_HISTORY + 5):
                store.add_job(DownloadJob(f"https://example.com/v/{n}"))
            self.assertEqual(len(store.jobs),MAX_HISTORY)
            self.assertEqual(len(AppStore(Path(d)).jobs),MAX_HISTORY)

    def test_corrupt_job_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d)
            atomic_json(d/"jobs.json",[{"url":"file:///tmp/a"},{"url":"https://example.com"}])
            self.assertEqual(len(AppStore(d).jobs),1)


class FakeEngine:
    def __init__(self):
        self.started = []
    def download(self,job,folder,event,cancel):
        self.started.append(job.id)
        event("progress",{"progress":25})
        for _ in range(12):
            if cancel.is_set(): raise JobCancelled()
            time.sleep(.004)
        if "bad" in job.url: raise RuntimeError("Simulated network issue")
        return {"title":"Finalizado", "file_path":""}

class CoordinatorTests(unittest.TestCase):
    def test_queue_sequential(self):
        events=[]
        engine=FakeEngine()
        c=DownloadCoordinator(engine,lambda jid,ty,p:events.append((jid,ty,p)),lambda:Path("/tmp"))
        jobs=[DownloadJob("https://example.com/a"),DownloadJob("https://example.com/b")]
        for j in jobs: c.enqueue(j)
        c.pending.join()
        self.assertEqual(engine.started,[j.id for j in jobs])
        self.assertEqual(len([e for e in events if e[1]=="complete"]),2)
        self.assertFalse(c.busy())

    def test_error(self):
        events=[]
        c=DownloadCoordinator(FakeEngine(),lambda jid,ty,p:events.append((jid,ty,p)),lambda:Path("/tmp"))
        c.enqueue(DownloadJob("https://example.com/bad"))
        c.pending.join()
        self.assertEqual(len([e for e in events if e[1]=="error"]),1)

    def test_cancel(self):
        events=[]
        c=DownloadCoordinator(FakeEngine(),lambda jid,ty,p:events.append((jid,ty,p)),lambda:Path("/tmp"))
        a=DownloadJob("https://example.com/a")
        c.enqueue(a)
        self.assertTrue(c.cancel(a.id))
        c.pending.join()
        self.assertIn("cancelled",[e[1] for e in events])


if __name__ == "__main__":
    unittest.main()
