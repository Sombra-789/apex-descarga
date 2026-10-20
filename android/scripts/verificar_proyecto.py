#!/usr/bin/env python3
"""Apex Descarga Android 1.0.1: static project checks; NOT an Android APK build."""
from pathlib import Path
from xml.etree import ElementTree as ET
import sys

root=Path(__file__).resolve().parents[1]
java=root/'app/src/main/java/com/apexvisualstudio/descarga'
manifest=ET.parse(root/'app/src/main/AndroidManifest.xml').getroot()
ns='{http://schemas.android.com/apk/res/android}'
app=manifest.find('application')
permissions={p.get(ns+'name') for p in manifest.findall('uses-permission')}
activities={a.get(ns+'name') for a in app.findall('activity')}
services={a.get(ns+'name') for a in app.findall('service')}
build=(root/'app/build.gradle').read_text()
checks=[]
def verify(ok,message): checks.append((bool(ok),message))
def src(name):return (java/(name+'.java')).read_text()

verify(app is not None,'Manifest app')
verify({'android.permission.INTERNET','android.permission.ACCESS_NETWORK_STATE',
        'android.permission.POST_NOTIFICATIONS','android.permission.FOREGROUND_SERVICE',
        'android.permission.FOREGROUND_SERVICE_DATA_SYNC'}<=permissions,'Permisos mínimos de red y segundo plano')
verify(not {'android.permission.MANAGE_EXTERNAL_STORAGE','android.permission.READ_MEDIA_VIDEO',
            'android.permission.QUERY_ALL_PACKAGES','android.permission.ACCESS_FINE_LOCATION'}&permissions,'Sin permisos amplios de archivos / localización')
verify(app.get(ns+'allowBackup')=='false' and app.get(ns+'usesCleartextTraffic')=='false','Backup y tráfico sin cifrar deshabilitados')
verify({' .MainActivity'.strip(),'.QueueActivity','.LibraryActivity','.ConverterActivity','.SettingsActivity'}<=activities,'Cinco pantallas')
verify('.DownloadService' in services and '.EngineUpdateJob' in services,'Servicio y actualizador')
verify('versionCode 9' in build and "versionName '1.0.1'" in build,'Versión 1.0.1')
verify("applicationId 'com.apexvisualstudio.descarga'" in build,'Mismo identificador de paquete')
verify('youtubedl-android:library:0.18.1' in build and 'youtubedl-android:ffmpeg:0.18.1' in build,'Dependencias de 0.4 conservadas')
verify('targetSdk 34' in build and 'minSdk 29' in build,'Android SDK compatible')
names=['EngineVersion','SettingsActivity','ThemeIdentity','MainActivity','NetworkPolicy','DownloadService','DownloadQueueStore','LibraryStore',
    'LibraryActivity','ConverterActivity','EngineUpdateJob','EngineHealth','DownloadStorage',
    'PrivacyTerms','MediaMetadata','ArtworkCache','ApexUi','QueueActivity']
verify(all((java/(n+'.java')).is_file() for n in names),'17 clases Java presentes')
verify(all('package com.apexvisualstudio.descarga;' in src(n) for n in names),'Paquete uniforme')
main=src('MainActivity');service=src('DownloadService');net=src('NetworkPolicy');store=src('DownloadQueueStore');health=src('EngineHealth')
verify('Intent.ACTION_SEND' in main and 'acceptShared(intent)' in main and 'sharedPending' in main,'Compartir enlaces y autoanalizar')
verify('ACCESS_NETWORK_STATE' in (root/'app/src/main/AndroidManifest.xml').read_text(),'Consulta de conectividad habilitada')
verify('NetworkCapabilities.TRANSPORT_WIFI' in net and 'wifi_only_v5' in net,'Preferencia solo Wi-Fi')
verify('NetworkPolicy.canStart(this)' in main and 'NetworkPolicy.canStart(this)' in service,'Enqueue y motor respetan red')
verify('wifiInterrupted=true' in service and 'destroyProcessById' in service and '"paused"' in service,'Interrupción tras pérdida de Wi-Fi')
verify('if(queue.next()!=null && NetworkPolicy.canStart(this))startDrain();' in service,'Sin bucle al esperar Wi-Fi')
verify('warn_mb_v5' in net and 'Uso de datos móviles' in main,'Advertencia por datos y umbral')
verify('estimatedBytes' in src('MediaMetadata') and 'estimated_bytes' in store,'Estimación de tamaño en metadata y cola')
verify('NetworkPolicy.hasSpace(this,estimate)' in service,'Comprobación de espacio previo')
verify('--embed-metadata' in service and '--embed-thumbnail' in service and '--convert-thumbnails' in service,'Carátula y etiquetas MP3')
verify('if(!fallback)' in service and '"mp3".equals(format)' in service,'Fallback MP3 sin carátula')
verify('EngineHealth.updateStable' in src('EngineUpdateJob') and 'EngineHealth.updateStable' in src('SettingsActivity'),'Actualización estable programada y manual')
verify('versionLooksValid' in health and 'engine_previous_version' in health and 'engine_update_issue' in health,'Diagnóstico de actualización, versión anterior')
verify('NETWORK_TYPE_UNMETERED' in src('EngineUpdateJob') and 'setRequiresBatteryNotLow(true)' in src('EngineUpdateJob'),'Actualizaciones condicionadas por red y batería')
verify('queueCard(' in src('ApexUi') and 'ArtworkCache.attach' in main,'Portadas y cola 0.4 conservadas')
verify('MEMORY' in src('ArtworkCache') and 'trimDiskCache' in src('ArtworkCache'),'Límite de caché de portadas')
verify('Reintentar' in src('QueueActivity') and 'resumePending' in store,'Reintento y recuperación de trabajos')
verify('Compartir' in src('LibraryActivity') and 'Eliminar' in src('LibraryActivity'),'Biblioteca completa')
verify('show_logo' in src('SettingsActivity') and 'custom_primary' in src('SettingsActivity'),'Paletas y ocultar logo')
verify((root/'app/src/main/res/drawable-nodpi/apex_brand.png').is_file(),'Identidad visual conservada')
verify('APEX_DESCARGA_ANDROID_1.0.1_DEBUG.apk' in (root/'scripts/generar_apk.ps1').read_text(encoding='utf-8-sig'),'Salida Windows 1.0.1')
verify('apex-descarga-android-1.0.1-' in (root.parent/'.github/workflows/build-and-test.yml').read_text(),'Artefacto Actions 1.0.1')
verify('py' not in (root/'app/src/main/AndroidManifest.xml').read_text().lower(),'Sin scripting externo en manifiesto')
verify('scaffold(this,"inicio")' in main and 'scaffold(this,"cola")' in src('QueueActivity') and 'scaffold(this,"biblioteca")' in src('LibraryActivity') and 'scaffold(this,"ajustes")' in src('SettingsActivity'), 'Navegación inferior en las cuatro pantallas')
verify('SharedPreferences' in src('ThemeIdentity') and 'onResume()' in src('QueueActivity'), 'Temas actualizados al volver de Ajustes')
for ok,desc in checks:print(('OK  ' if ok else 'FAIL ')+desc)
print(f'\n{sum(ok for ok,_ in checks)}/{len(checks)} comprobaciones estáticas superadas')
if not all(ok for ok,_ in checks):sys.exit(1)
print('NOTA: no sustituye una compilación Gradle ni pruebas en dispositivo Android.')

