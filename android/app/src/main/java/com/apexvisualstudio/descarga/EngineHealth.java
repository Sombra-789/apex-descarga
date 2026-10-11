package com.apexvisualstudio.descarga;

import android.content.Context;
import android.content.SharedPreferences;
import com.yausername.youtubedl_android.YoutubeDL;
import java.util.Locale;

/** Only the wrapper's upstream STABLE updater is used: no arbitrary remote executable URLs.
 * Runtime reports version before/after. This is NOT an independent cryptographic signature
 * check and does NOT promise rollback of yt-dlp internals.
 */
public final class EngineHealth {
    private EngineHealth(){}
    public static boolean versionLooksValid(String version){
        return version!=null && version.matches("20[0-9]{2}\\.[0-9]{1,2}\\.[0-9]{1,2}(?:[-.+].*)?");
    }
    public static String updateStable(Context context) throws Exception {
        SharedPreferences prefs=context.getSharedPreferences("apex_descarga",Context.MODE_PRIVATE);
        synchronized(DownloadService.ENGINE_LOCK){
            YoutubeDL engine=YoutubeDL.getInstance();
            engine.init(context.getApplicationContext());
            String old=engine.versionName(context);
            prefs.edit().putString("engine_previous_version",old==null?"":old)
                .putLong("engine_last_checked",System.currentTimeMillis()).apply();
            try{
                engine.updateYoutubeDL(context,YoutubeDL.UpdateChannel._STABLE);
                String after=engine.versionName(context);
                if(!versionLooksValid(after)){
                    throw new IllegalStateException("No se pudo verificar la versión publicada por yt-dlp");
                }
                prefs.edit().putString("engine_version_last",after)
                    .putString("engine_update_issue","")
                    .putLong("engine_updated_at",System.currentTimeMillis()).apply();
                return after;
            }catch(Exception ex){
                prefs.edit().putString("engine_update_issue",ex.getClass().getSimpleName()).apply();
                throw ex;
            }
        }
    }
}
