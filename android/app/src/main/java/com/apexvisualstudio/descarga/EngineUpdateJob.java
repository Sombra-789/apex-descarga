package com.apexvisualstudio.descarga;

import android.app.job.JobInfo;
import android.app.job.JobParameters;
import android.app.job.JobScheduler;
import android.app.job.JobService;
import android.content.ComponentName;
import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;
import com.yausername.youtubedl_android.YoutubeDL;

/** Auto updates STABLE yt-dlp on unmetered networks about once per week.
 * Android may delay jobs due to Doze, battery saver and scheduling constraints.
 */
public final class EngineUpdateJob extends JobService {
    private static final int JOB_ID=90217;
    public static void schedule(Context context){
        SharedPreferences p=context.getSharedPreferences("apex_descarga",Context.MODE_PRIVATE);
        if(!p.getBoolean("auto_engine_update",true)){
            ((JobScheduler)context.getSystemService(Context.JOB_SCHEDULER_SERVICE)).cancel(JOB_ID);
            return;
        }
        JobScheduler jobs=(JobScheduler)context.getSystemService(Context.JOB_SCHEDULER_SERVICE);
        if(jobs==null)return;
        for(JobInfo j:jobs.getAllPendingJobs())if(j.getId()==JOB_ID)return;
        JobInfo spec=new JobInfo.Builder(JOB_ID,new ComponentName(context,EngineUpdateJob.class))
            .setRequiredNetworkType(JobInfo.NETWORK_TYPE_UNMETERED)
            .setPeriodic(7L*24*60*60*1000)
            .setRequiresBatteryNotLow(true)
            .build();
        jobs.schedule(spec);
    }
    @Override public boolean onStartJob(JobParameters params){
        new Thread(()->{
            try{
                // Avoid replacing the engine while a transfer is in progress.
                org.json.JSONArray jobs=new DownloadQueueStore(this).all();
                boolean active=false;
                for(int k=0;k<jobs.length();k++){
                    org.json.JSONObject item=jobs.optJSONObject(k);
                    if(item!=null&&"running".equals(item.optString("status")))active=true;
                }
                if(active){Log.i("ApexUpdate","Hay una descarga activa; posponer actualización");}
                else EngineHealth.updateStable(getApplicationContext());
            }catch(Exception ex){ Log.w("ApexUpdate","Actualización automática pospuesta",ex); }
            finally{jobFinished(params,false);}
        },"ApexEngineUpdate").start();
        return true;
    }
    @Override public boolean onStopJob(JobParameters params){return true;}
}
