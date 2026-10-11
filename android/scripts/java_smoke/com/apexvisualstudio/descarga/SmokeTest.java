package com.apexvisualstudio.descarga;
import android.content.Context;
public class SmokeTest {
 private static int passed=0;
 private static void yes(boolean v,String message){if(!v)throw new AssertionError(message);passed++;}
 public static void main(String[] args)throws Exception{
  Context c=new Context();
  yes(!NetworkPolicy.wifiOnly(c),"defaults to mobile allowed");
  c.getSharedPreferences("apex_descarga",0).edit().putBoolean(NetworkPolicy.WIFI_ONLY,true).apply();
  yes(!NetworkPolicy.canStart(c),"wifi only blocks mobile");
  c.network.wifi=true;
  yes(NetworkPolicy.canStart(c),"wifi only allows wifi");
  yes(NetworkPolicy.isWifi(c),"wifi detection");
  yes(NetworkPolicy.warnMB(c)==100,"default warning threshold");
  yes(NetworkPolicy.hasSpace(c,10L*1024*1024),"sufficient temporary space");
  yes(NetworkPolicy.displaySize(1024*1024).equals("1.0 MB"),"size format");
  yes(MediaMetadata.urlThumbnail("https://www.youtube.com/watch?v=Xo9dQ_QD7K8").contains("Xo9dQ_QD7K8"),"youtube art");
  yes(MediaMetadata.urlThumbnail("https://youtube.com/shorts/Xo9dQ_QD7K8").contains("Xo9dQ_QD7K8"),"shorts art");
  yes(MediaMetadata.urlThumbnail("https://evil.org/watch?v=Xo9dQ_QD7K8").isEmpty(),"reject other domains");
  yes(EngineHealth.versionLooksValid("2026.08.19"),"official version syntax");
  yes(!EngineHealth.versionLooksValid("not-a-version"),"invalid version");
  yes(EngineHealth.updateStable(c).equals("2026.08.19"),"version checked after update");
  System.out.println("OK "+passed+" Java smoke assertions");
 }
}
