package com.apexvisualstudio.descarga;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/** Private, persistent queue. Only one foreground-service worker consumes jobs. */
public final class DownloadQueueStore {
    private static final String PREF = "apex_descarga";
    private static final Object GLOBAL_LOCK = new Object();
    private static final String KEY = "queue_v3";
    private final SharedPreferences prefs;

    public DownloadQueueStore(Context context) {
        prefs = context.getApplicationContext().getSharedPreferences(PREF, Context.MODE_PRIVATE);
    }

    public synchronized JSONArray all() { synchronized (GLOBAL_LOCK) {
        try { return new JSONArray(prefs.getString(KEY, "[]")); }
        catch (Exception ignored) { return new JSONArray(); }
     }}

    private synchronized void save(JSONArray list) { synchronized (GLOBAL_LOCK) { prefs.edit().putString(KEY, list.toString()).commit();  }}

    public synchronized int pendingCount() { synchronized (GLOBAL_LOCK) {
        int count = 0;
        JSONArray list = all();
        for (int i=0; i<list.length(); i++) {
            JSONObject item = list.optJSONObject(i);
            if (item != null && ("waiting".equals(item.optString("status")) || "running".equals(item.optString("status")))) count++;
        }
        return count;
     }}

    public synchronized String add(String url, String format, int quality, boolean hls) { synchronized (GLOBAL_LOCK) {
        if (pendingCount() >= 15) return null;
        JSONArray list = all();
        JSONObject job = new JSONObject();
        String id = UUID.randomUUID().toString();
        try {
            job.put("id", id); job.put("url", url); job.put("format", format);
            job.put("quality", quality); job.put("hls", hls); job.put("status", "waiting");
            job.put("progress", 0); job.put("name", hostName(url)); job.put("note", "En cola");
            job.put("title", hostName(url)); job.put("author", ""); job.put("thumbnail", MediaMetadata.urlThumbnail(url));
            job.put("platform", hostName(url));job.put("duration", "");job.put("qualities", "");job.put("estimated_bytes",0L);
            job.put("created", System.currentTimeMillis()); list.put(job);
            save(list); return id;
        } catch (Exception ex) { return null; }
     }}

    /** Persist analyzed metadata for every matching queue entry, even after a restart. */
    public synchronized void applyMetadata(String url,MediaMetadata m) { synchronized(GLOBAL_LOCK){
        JSONArray entries=all();boolean changed=false;
        for(int i=0;i<entries.length();i++){
            JSONObject j=entries.optJSONObject(i);
            if(j!=null&&url.equals(j.optString("url"))){
                try{
                    j.put("title",m.title);j.put("author",m.author);j.put("thumbnail",m.thumbnail);
                    j.put("platform",m.platform);j.put("duration",m.duration);j.put("qualities",m.qualities);
                    j.put("estimated_bytes",m.estimatedBytes);
                    changed=true;
                }catch(Exception ignored){}
            }
        }
        if(changed)save(entries);
    }}

    public synchronized void complete(String id,String label,String name,String uri) { synchronized(GLOBAL_LOCK){
        JSONArray entries=all();
        for(int i=0;i<entries.length();i++){
            JSONObject j=entries.optJSONObject(i);if(j==null||!id.equals(j.optString("id")))continue;
            try{j.put("status","done");j.put("progress",100);j.put("note",label);
                j.put("name",name);j.put("uri",uri);}catch(Exception ignored){}
            break;
        }
        save(entries);
    }}

    /** Retry a finished or interrupted item without creating duplicate entries. */
    public synchronized boolean retry(String id) { synchronized(GLOBAL_LOCK){
        JSONArray entries=all();
        for(int i=0;i<entries.length();i++){
            JSONObject j=entries.optJSONObject(i);if(j==null||!id.equals(j.optString("id")))continue;
            String status=j.optString("status");
            if(!("failed".equals(status)||"cancelled".equals(status)||"paused".equals(status)))return false;
            if(pendingCount()>=15)return false;
            try{j.put("status","waiting");j.put("progress",0);j.put("note","En cola otra vez");j.remove("uri");}catch(Exception ignored){}
            save(entries);return true;
        }
        return false;
    }}

    public synchronized JSONObject findById(String id){ synchronized(GLOBAL_LOCK){
        JSONArray list=all();for(int i=0;i<list.length();i++){
            JSONObject j=list.optJSONObject(i);if(j!=null&&id.equals(j.optString("id")))return j;
        }
        return null;
    }}

    public synchronized JSONObject next() { synchronized (GLOBAL_LOCK) {
        JSONArray list = all();
        for (int i=0; i<list.length(); i++) {
            JSONObject job = list.optJSONObject(i);
            if (job != null && "waiting".equals(job.optString("status"))) return job;
        }
        return null;
     }}

    public synchronized void update(String id, String status, int percent, String note, String name) { synchronized (GLOBAL_LOCK) {
        JSONArray list = all();
        for (int i=0; i<list.length(); i++) {
            JSONObject job = list.optJSONObject(i);
            if (job == null || !id.equals(job.optString("id"))) continue;
            try {
                if (status != null) job.put("status", status);
                if (percent >= 0) job.put("progress", percent);
                if (note != null) job.put("note", note.length() > 140 ? note.substring(0,140) : note);
                if (name != null) job.put("name", name);
            } catch (Exception ignored) {}
            break;
        }
        save(list);
     }}

    public synchronized boolean cancelPending(String id) { synchronized (GLOBAL_LOCK) {
        JSONArray list = all();
        for (int i=0; i<list.length(); i++) {
            JSONObject job = list.optJSONObject(i);
            if (job == null || !id.equals(job.optString("id"))) continue;
            if ("waiting".equals(job.optString("status"))) {
                try { job.put("status", "cancelled"); job.put("note", "Cancelado antes de empezar"); } catch (Exception ignored) {}
                save(list); return true;
            }
        }
        return false;
     }}

    public synchronized void markInterrupted() { synchronized (GLOBAL_LOCK) {
        JSONArray list = all();
        boolean dirty = false;
        for (int i=0; i<list.length(); i++) {
            JSONObject job = list.optJSONObject(i);
            if (job != null && "running".equals(job.optString("status"))) {
                try { job.put("status", "paused"); job.put("note", "Interrumpida por Android; reanúdala manualmente"); dirty=true; }
                catch (Exception ignored) {}
            }
        }
        if (dirty) save(list);
     }}

    public synchronized void resumePending() { synchronized (GLOBAL_LOCK) {
        JSONArray list = all();
        boolean dirty=false;
        for (int i=0; i<list.length(); i++) {
            JSONObject job=list.optJSONObject(i);
            if(job!=null && "paused".equals(job.optString("status"))) {
                try {job.put("status","waiting");job.put("progress",0);job.put("note","En cola otra vez");dirty=true;}
                catch(Exception ignored){}
            }
        }
        if(dirty)save(list);
     }}

    public synchronized void clearFinished() { synchronized (GLOBAL_LOCK) {
        JSONArray list = all(), keep = new JSONArray();
        for (int i=0; i<list.length(); i++) {
            JSONObject job=list.optJSONObject(i);
            if (job == null) continue;
            String s=job.optString("status");
            if ("running".equals(s)||"waiting".equals(s)||"paused".equals(s)) keep.put(job);
        }
        save(keep);
     }}

    private static String hostName(String url) {
        try { return new java.net.URI(url).getHost(); }
        catch (Exception ex) { return "Contenido"; }
    }
}
