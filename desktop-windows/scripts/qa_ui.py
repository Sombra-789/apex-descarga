"""Prueba visual básica sin Internet; requiere entorno gráfico Tk disponible."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from apex_desktop.models import DownloadJob
from apex_desktop.storage import AppStore
from apex_desktop.ui_pro import DesktopApp

class FakeEngine:
    def probe(self,url):
        return {"title":"Medio de prueba","uploader":"QA","duration":91,"thumbnail":""}
    def download(self,*args,**kwargs):
        return {}


def run():
    with tempfile.TemporaryDirectory(prefix="apex-ui-qa-") as dirname:
        store=AppStore(Path(dirname))
        for state in ("pendiente","completado","error"):
            store.add_job(DownloadJob(f"https://example.com/{state}",title="Prueba "+state,state=state,
                                      progress=100 if state=="completado" else 0))
        app=DesktopApp(store=store,engine=FakeEngine())
        try:
            for page in ("inicio","cola","biblioteca","ajustes","acerca"):
                app.navigate(page)
                app.update_idletasks()
                app.update()
                assert app.page==page, page
                print("OK GUI",page)
            app.navigate("biblioteca")
            app._filter_library("Todos")
            app._search_library("Prueba")
            app.update()
            app._change_theme("Cian","#1BC8DB")
            app.update()
            assert store.settings["accent"]=="#1BC8DB"
            app.navigate("ajustes")
            app.compact_value.set(True)
            app._set_compact()
            assert AppStore(Path(dirname)).settings["compact_mode"] is True
            print("OK GUI ajustes, datos y filtros")
        finally:
            app.destroy()

if __name__=="__main__":
    run()
