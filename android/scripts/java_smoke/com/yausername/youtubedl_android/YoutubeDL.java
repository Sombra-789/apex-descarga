package com.yausername.youtubedl_android;
import android.content.Context;
public class YoutubeDL {
 public enum UpdateChannel {_STABLE}
 private static final YoutubeDL instance=new YoutubeDL();
 public static YoutubeDL getInstance(){return instance;}
 public Object getInfo(String url){return null;}
 public void init(Context c){};
 public String versionName(Context c){return "2026.08.19";}
 public void updateYoutubeDL(Context c,UpdateChannel channel){}
}
