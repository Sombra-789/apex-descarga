package com.apexvisualstudio.descarga;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;
import org.json.JSONArray;
import org.json.JSONObject;

/** Local-only index of media created by this app; never probes other apps' storage. */
public final class LibraryStore {
    private static final String KEY = "media_library_v3";
    private final SharedPreferences prefs;
    public LibraryStore(Context c) { prefs=c.getApplicationContext().getSharedPreferences("apex_descarga",Context.MODE_PRIVATE); }
    public synchronized JSONArray all(){
        try {return new JSONArray(prefs.getString(KEY,"[]"));}
        catch(Exception ex){return new JSONArray();}
    }
    public synchronized void add(String name, Uri uri, String mime){add(name,uri,mime,null);}
    public synchronized void add(String name, Uri uri, String mime, JSONObject job){
        JSONArray previous=all(), next=new JSONArray();
        JSONObject obj=new JSONObject();
        try {obj.put("name",name);obj.put("uri",uri.toString());obj.put("mime",mime);obj.put("when",System.currentTimeMillis());
            if(job!=null){
                for(String k:new String[]{"title","thumbnail","author","duration","platform","qualities"})
                    obj.put(k,job.optString(k,""));
            }
            next.put(obj);}catch(Exception ignored){}
        for(int i=0;i<Math.min(previous.length(),79);i++)next.put(previous.opt(i));
        prefs.edit().putString(KEY,next.toString()).apply();
    }
    public synchronized void remove(String uri){
        JSONArray old=all(), fresh=new JSONArray();
        for(int i=0;i<old.length();i++){
            JSONObject obj=old.optJSONObject(i);
            if(obj!=null&&!uri.equals(obj.optString("uri")))fresh.put(obj);
        }
        prefs.edit().putString(KEY,fresh.toString()).apply();
    }
    public synchronized void clear(){prefs.edit().remove(KEY).apply();}
}
