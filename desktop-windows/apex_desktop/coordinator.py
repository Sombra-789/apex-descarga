"""Cola secuencial sin operaciones de GUI fuera del hilo principal."""
from __future__ import annotations

import queue
import threading
from pathlib import Path
from typing import Callable

from .engine import JobCancelled, MediaEngine
from .models import DownloadJob


class DownloadCoordinator:
    def __init__(self, engine: MediaEngine, notify: Callable[[str, str, dict], None], folder: Callable[[], Path]):
        self.engine = engine
        self.notify = notify
        self.folder = folder
        self.pending: queue.Queue[tuple[str, DownloadJob]] = queue.Queue()
        self.cancels: dict[str, threading.Event] = {}
        self.lock = threading.Lock()
        self.worker = threading.Thread(target=self._run, name="ApexDownloadQueue", daemon=True)
        self.worker.start()

    def enqueue(self, job: DownloadJob):
        with self.lock:
            if job.id in self.cancels:
                return
            flag = threading.Event()
            self.cancels[job.id] = flag
        self.pending.put((job.id, job))

    def cancel(self, job_id: str) -> bool:
        with self.lock:
            flag = self.cancels.get(job_id)
            if flag:
                flag.set()
                return True
        return False

    def busy(self) -> bool:
        with self.lock:
            return bool(self.cancels)

    def _run(self):
        while True:
            job_id, job = self.pending.get()
            try:
                with self.lock:
                    flag = self.cancels.get(job_id)
                if flag is None or flag.is_set():
                    self.notify(job_id, "cancelled", {})
                    continue
                self.notify(job_id, "state", {"state": "descargando"})
                try:
                    result = self.engine.download(
                        job, self.folder(),
                        lambda typ, data: self.notify(job_id, typ, data),
                        flag,
                    )
                except JobCancelled:
                    self.notify(job_id, "cancelled", {})
                except Exception as exc:
                    if flag.is_set():
                        self.notify(job_id, "cancelled", {})
                    else:
                        # yt-dlp puede incluir rutas privadas: no imprimir diagnósticos completos.
                        self.notify(job_id, "error", {"error": str(exc)[:500]})
                else:
                    if flag.is_set():
                        self.notify(job_id, "cancelled", {})
                    else:
                        self.notify(job_id, "complete", result)
            finally:
                with self.lock:
                    self.cancels.pop(job_id, None)
                self.pending.task_done()
