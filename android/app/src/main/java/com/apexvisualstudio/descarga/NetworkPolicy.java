package com.apexvisualstudio.descarga;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.os.Environment;
import android.os.StatFs;
import java.io.File;

/** Offline configuration, network/battery-safe checks. No analytics or device identifiers. */
public final class NetworkPolicy {
    public static final String PREF="apex_descarga";
    public static final String WIFI_ONLY="wifi_only_v5";
    public static final String WARN_MB="warn_mb_v5";
    public static final long MB=1024L*1024;
    private NetworkPolicy(){}
    public static SharedPreferences prefs(Context ctx){
        return ctx.getApplicationContext().getSharedPreferences(PREF,Context.MODE_PRIVATE);
    }
    public static boolean wifiOnly(Context ctx){return prefs(ctx).getBoolean(WIFI_ONLY,false);}
    public static int warnMB(Context ctx){return prefs(ctx).getInt(WARN_MB,100);}
    public static boolean isWifi(Context ctx){
        ConnectivityManager manager=(ConnectivityManager)ctx.getSystemService(Context.CONNECTIVITY_SERVICE);
        if(manager==null)return false;
        Network net=manager.getActiveNetwork();
        NetworkCapabilities caps=net==null?null:manager.getNetworkCapabilities(net);
        return caps!=null&&caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            &&caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI);
    }
    public static boolean isMetered(Context ctx){
        ConnectivityManager m=(ConnectivityManager)ctx.getSystemService(Context.CONNECTIVITY_SERVICE);
        return m==null || m.isActiveNetworkMetered();
    }
    public static boolean canStart(Context ctx){return !wifiOnly(ctx)||isWifi(ctx);}
    /** True if even a safe minimum of temporary working space is missing. */
    public static boolean hasSpace(Context ctx,long estimate){
        try{
            File path=ctx.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
            if(path==null)path=ctx.getFilesDir();
            StatFs fs=new StatFs(path.getAbsolutePath());
            long available=fs.getAvailableBytes();
            long expected=estimate>0?Math.min(Long.MAX_VALUE/2,estimate)*2:96L*MB;
            return available>expected+64L*MB;
        }catch(Exception ex){return true;}
    }
    public static String displaySize(long bytes){
        if(bytes<=0)return "Tamaño no disponible";
        return String.format(java.util.Locale.ROOT,"%.1f MB",(double)bytes/MB);
    }
}
