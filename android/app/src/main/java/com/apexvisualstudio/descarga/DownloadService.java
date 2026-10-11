package com.apexvisualstudio.descarga;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.Context;
import android.net.Uri;
import android.os.Build;
import android.os.IBinder;
import android.os.SystemClock;
import android.util.Log;

import com.yausername.ffmpeg.FFmpeg;
import com.yausername.youtubedl_android.YoutubeDL;
import com.yausername.youtubedl_android.YoutubeDLRequest;

import org.json.JSONObject;

import java.io.File;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Locale;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/** Serial background transfers with an Android foreground notification (dataSync).
 * Queue is private and durable; running jobs become paused if Android kills the process.
 */
public final class DownloadService extends Service {
    public static final String ADD = "com.apexvisualstudio.descarga.ADD";
    public static final String CANCEL = "com.apexvisualstudio.descarga.CANCEL";
    public static final String CHANGED = "com.apexvisualstudio.descarga.CHANGED";
    public static final String EXTRA_ID = "id";
    public static final Object ENGINE_LOCK = new Object();
    private static final String CHANNEL = "apex_downloads";
    private static final int NOTIFICATION_ID = 311;

    private final ExecutorService executor=Executors.newSingleThreadExecutor();
    private final AtomicBoolean draining=new AtomicBoolean(false);
    private volatile String runningId=null, processId=null;
    private volatile boolean stopRequested=false, wifiInterrupted=false;
    private volatile long lastNotify=0;
    private DownloadQueueStore queue;
    private DownloadStorage storage;
    private LibraryStore library;

    public static void enqueue(Context c) {
        Intent i=new Intent(c,DownloadService.class);i.setAction(ADD);
        if(Build.VERSION.SDK_INT>=26)c.startForegroundService(i); else c.startService(i);
    }
    public static void cancel(Context c,String id) {
        Intent i=new Intent(c,DownloadService.class);i.setAction(CANCEL);i.putExtra(EXTRA_ID,id);
        // A cancellation can also arrive when only pending jobs exist.
        if(Build.VERSION.SDK_INT>=26)c.startForegroundService(i); else c.startService(i);
    }
    @Override public void onCreate(){
        super.onCreate();
        queue=new DownloadQueueStore(this);
        storage=new DownloadStorage(this);
        library=new LibraryStore(this);
        queue.markInterrupted();
        if(Build.VERSION.SDK_INT>=26){
            NotificationChannel ch=new NotificationChannel(CHANNEL,"Descargas de Apex",NotificationManager.IMPORTANCE_LOW);
            ch.setDescription("Progreso de descargas autorizadas");
            getSystemService(NotificationManager.class).createNotificationChannel(ch);
        }
    }
    @Override public int onStartCommand(Intent intent,int flags,int startId){
        String action=intent==null?ADD:intent.getAction();
        // startForeground immediately (mandatory following startForegroundService).
        startForeground(NOTIFICATION_ID, notification("Preparando descargas",0,true));
        if(CANCEL.equals(action)){
            String id=intent.getStringExtra(EXTRA_ID);
            if(id!=null){
                if(id.equals(runningId)){
                    stopRequested=true;
                    final String current=processId;
                    new Thread(()->{if(current!=null)try{YoutubeDL.getInstance().destroyProcessById(current);}catch(Exception ignored){}},"ApexCancel").start();
                } else {queue.cancelPending(id); sendChanged();}
            }
        }
        startDrain();
        return START_NOT_STICKY;
    }
    private void startDrain(){
        if(!draining.compareAndSet(false,true))return;
        executor.execute(()->{
            try {
                synchronized(ENGINE_LOCK){
                    YoutubeDL.getInstance().init(getApplicationContext());
                    FFmpeg.getInstance().init(getApplicationContext());
                }
                for(;;){
                    if(!NetworkPolicy.canStart(this)){
                        // Leave pending jobs intact until user resumes while on Wi-Fi.
                        break;
                    }
                    JSONObject job=queue.next();
                    if(job==null)break;
                    runJob(job);
                }
            }catch(Exception ex){
                Log.e("ApexService","Motor no disponible",ex);
                queue.markInterrupted();sendChanged();
            }finally{
                draining.set(false);
                if(queue.next()!=null && NetworkPolicy.canStart(this))startDrain();
                else {
                    stopForeground(STOP_FOREGROUND_REMOVE);
                    stopSelf();
                }
            }
        });
    }
    private void runJob(JSONObject job){
        String id=job.optString("id");
        String format=job.optString("format","mp4");
        int quality=job.optInt("quality",3);
        boolean hls=job.optBoolean("hls",false);
        String url=job.optString("url");
        if(id.isEmpty()||url.isEmpty())return;
        runningId=id; stopRequested=false;wifiInterrupted=false;
        if(!NetworkPolicy.canStart(this)){
            queue.update(id,"paused",0,"Esperando Wi-Fi · reanudar al conectarse",null);
            sendChanged();runningId=null;return;
        }
        queue.update(id,"running",0,"Conectando…",null);sendChanged();
        File temp=null;
        try{
            // Metadata is best effort. A platform can allow downloads but reject metadata.
            if(job.optString("author","").isEmpty()){
                try{
                    MediaMetadata m;
                    synchronized(ENGINE_LOCK){m=MediaMetadata.fetch(url);}
                    queue.applyMetadata(url,m);
                    JSONObject refreshed=queue.findById(id);if(refreshed!=null)job=refreshed;
                    sendChanged();
                }catch(Exception ignored){}
            }
            long estimate=job.optLong("estimated_bytes",0);
            if(!NetworkPolicy.hasSpace(this,estimate))
                throw new IllegalStateException("No hay suficiente espacio temporal para esta descarga.");
            temp=storage.createJobDirectory();
            File media=null;boolean usedFallback=false;
            // MP3 attempt 1 embeds title/artist/cover. If a postprocessor or site fails,
            // attempt 2 prioritizes successful audio extraction without enrichment.
            int attempts=2;
            for(int attempt=0;attempt<attempts;attempt++){
                if(stopRequested)throw new InterruptedException("Cancelada");
                File part=new File(temp,"intento_"+(attempt+1));
                if(!part.mkdirs())throw new IllegalStateException("No se pudo preparar la carpeta temporal");
                YoutubeDLRequest req=makeRequest(url,format,quality,hls,attempt>0,part);
                processId="apex-"+UUID.randomUUID();
                final boolean fallback=attempt>0;
                try{
                    synchronized(ENGINE_LOCK){
                        YoutubeDL.getInstance().execute(req,processId,(pct,eta,line)->{
                            if(stopRequested||wifiInterrupted)return kotlin.Unit.INSTANCE;
                            if(NetworkPolicy.wifiOnly(this)&&!NetworkPolicy.isWifi(this)){
                                wifiInterrupted=true;
                                final String interruptedProcess=processId;
                                new Thread(()->{
                                    try {YoutubeDL.getInstance().destroyProcessById(interruptedProcess);}
                                    catch(Exception ignored){}
                                },"ApexWifiStop").start();
                                return kotlin.Unit.INSTANCE;
                            }
                            int p=Math.max(0,Math.min(99,pct.intValue()));
                            String msg=fallback?"Alternativa":"Descargando";
                            String details=progressDetails(line,eta);
                            long now=SystemClock.elapsedRealtime();
                            if(now-lastNotify>900 || p>=99){
                                lastNotify=now;
                                queue.update(id,"running",p,msg+" · "+p+"%"+details,null);
                                showProgress(p,msg);sendChanged();
                            }
                            return kotlin.Unit.INSTANCE;
                        });
                    }
                    if(wifiInterrupted)throw new InterruptedException("Wi-Fi perdido");
                    if(stopRequested)throw new InterruptedException("Cancelada");
                    media=locateMedia(part,format);
                    if(media==null)throw new IllegalStateException("El motor no generó un archivo "+format);
                    usedFallback=fallback;break;
                }catch(Exception err){
                    if(wifiInterrupted)throw new InterruptedException("Wi-Fi perdido");
                    if(stopRequested)throw new InterruptedException("Cancelada");
                    if(attempt==0&&(canRetry(err)||"mp3".equals(format))){
                        queue.update(id,"running",0,"Buscando calidad alternativa…",null);sendChanged();
                    }else throw err;
                }
            }
            if(stopRequested)throw new InterruptedException("Cancelada");
            if(media==null)throw new IllegalStateException("No se generó un archivo válido");
            queue.update(id,"running",99,"Guardando archivo…",null);sendChanged();
            Uri uri=storage.publish(media);
            library.add(media.getName(),uri,"mp3".equals(format)?"audio/mpeg":"video/mp4",job);
            String note=usedFallback?("mp3".equals(format)?"Completada · audio sin portada":"Completada · Mejor disponible")
                :"Descarga completada";
            queue.complete(id,note,media.getName(),uri.toString());
        }catch(InterruptedException ex){
            if(wifiInterrupted)queue.update(id,"paused",0,"Wi-Fi desconectado · reanudar al reconectar",null);
            else queue.update(id,"cancelled",0,"Descarga cancelada",null);
        }catch(Exception ex){
            String msg=errorMessage(ex);
            queue.update(id,"failed",0,msg,null);
            getSharedPreferences("apex_descarga",MODE_PRIVATE).edit().putString("last_error_v3",String.valueOf(ex)).apply();
            Log.e("ApexService","Error de descarga",ex);
        }finally{
            DownloadStorage.cleanup(temp);
            processId=null;runningId=null;stopRequested=false;wifiInterrupted=false;
            sendChanged();
        }
    }
    /** Keep download details readable instead of displaying the raw yt-dlp console. */
    private static String progressDetails(String line,Object etaValue){
        long eta=etaValue instanceof Number?((Number)etaValue).longValue():-1;
        if(line==null)line="";
        java.util.regex.Matcher speed=java.util.regex.Pattern.compile("(?i)\\bat\\s+([0-9.]+[KMGT]?i?B/s)").matcher(line);
        String rate=speed.find()?" · "+speed.group(1):"";
        java.util.regex.Matcher total=java.util.regex.Pattern.compile("(?i)\\bof\\s+([0-9.]+[KMGT]?i?B)").matcher(line);
        if(total.find())rate=" · "+total.group(1)+rate;
        if(eta>0&&eta<86400)rate+=" · "+(eta/60)+":"+String.format(Locale.ROOT,"%02d",eta%60)+" restantes";
        return rate;
    }
    private YoutubeDLRequest makeRequest(String url,String format,int quality,boolean hls,boolean fallback,File dir){
        YoutubeDLRequest req=new YoutubeDLRequest(url);
        req.addOption("--no-playlist");req.addOption("--no-mtime");req.addOption("--newline");
        req.addOption("--restrict-filenames");req.addOption("--no-overwrites");
        req.addOption("-o",new File(dir,"%(title).90B [%(id)s].%(ext)s").getAbsolutePath());
        if("mp3".equals(format)){
            req.addOption("-f","bestaudio/best");
            req.addOption("--extract-audio");req.addOption("--audio-format","mp3");req.addOption("--audio-quality","0");
            if(!fallback){
                // yt-dlp extracts ID3 title, artist, and embeds source artwork when available.
                req.addOption("--embed-metadata");
                req.addOption("--write-thumbnail");
                req.addOption("--convert-thumbnails","jpg");
                req.addOption("--embed-thumbnail");
            }
        }else{
            String bound=quality==0?"":"[height<="+new int[]{0,480,720,1080,2160}[Math.min(4,Math.max(0,quality))]+"]";
            String stable="bv"+bound+"[vcodec^=avc1]+ba[acodec^=mp4a]/bv"+bound+"[ext=mp4]+ba[ext=m4a]/b"+bound+"[ext=mp4]";
            String transport="bv"+bound+"[protocol*=m3u8]+ba[protocol*=m3u8]/b"+bound;
            if(fallback){
                // Never exceed requested quality when a limit is selected.
                req.addOption("-f","bv"+bound+"+ba/b"+bound+"/best"+bound);
            }else req.addOption("-f",hls?transport:stable);
            req.addOption("--merge-output-format","mp4");
        }
        return req;
    }
    private static boolean canRetry(Exception ex){
        String s=String.valueOf(ex).toLowerCase(Locale.ROOT);
        return s.contains("requested format")||s.contains("not available")||s.contains("403")||s.contains("forbidden")||s.contains("download video data");
    }
    private static String errorMessage(Exception ex){
        String s=String.valueOf(ex.getMessage());
        if(s.contains("403"))return "El sitio rechazó el formato (403). Prueba HLS u otra calidad.";
        if(s.toLowerCase(Locale.ROOT).contains("unsupported url"))return "El enlace no apunta a contenido compatible.";
        if(s.toLowerCase(Locale.ROOT).contains("format"))return "Formato no disponible en este contenido.";
        // Warnings are not failures. Preserve the real error when present.
        int index=s.lastIndexOf("ERROR:");
        if(index>=0)s=s.substring(index);
        else if(s.toLowerCase(Locale.ROOT).startsWith("warning:"))s="Falló la descarga. Consulta el registro para detalles.";
        return s.length()>120?s.substring(0,120)+"…":s;
    }
    private static File locateMedia(File dir,String format){
        File[] files=dir.listFiles(f->f.isFile()&&f.length()>0&&f.getName().toLowerCase(Locale.ROOT).endsWith("."+format));
        return files==null?null:Arrays.stream(files).max(Comparator.comparingLong(File::length)).orElse(null);
    }
    private Notification notification(String message,int progress,boolean indeterminate){
        Intent target=new Intent(this,MainActivity.class);
        PendingIntent content=PendingIntent.getActivity(this,0,target,PendingIntent.FLAG_IMMUTABLE|PendingIntent.FLAG_UPDATE_CURRENT);
        Notification.Builder b=Build.VERSION.SDK_INT>=26?new Notification.Builder(this,CHANNEL):new Notification.Builder(this);
        b.setContentTitle("Apex Descarga").setContentText(message)
            .setSmallIcon(R.drawable.ic_apex_notification)
            .setContentIntent(content).setOngoing(true).setOnlyAlertOnce(true)
            .setProgress(100,progress,indeterminate);
        return b.build();
    }
    private void showProgress(int percent,String label){
        NotificationManager nm=(NotificationManager)getSystemService(NOTIFICATION_SERVICE);
        nm.notify(NOTIFICATION_ID,notification(label+" · "+percent+"%",percent,false));
    }
    private void sendChanged(){
        Intent event=new Intent(CHANGED);event.setPackage(getPackageName());sendBroadcast(event);
    }
    @Override public IBinder onBind(Intent intent){return null;}
    @Override public void onDestroy(){executor.shutdownNow();super.onDestroy();}
}
