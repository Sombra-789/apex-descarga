package com.apexvisualstudio.descarga;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Handler;
import android.os.Looper;
import android.util.Size;
import android.widget.ImageView;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.URI;
import java.net.URL;
import java.security.MessageDigest;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Small, private thumbnail cache; remote URLs never go into intents or logs. */
public final class ArtworkCache {
    private static final int MAX_BYTES=2_000_000;
    private static final ExecutorService IO=Executors.newFixedThreadPool(3);
    private static final Handler MAIN=new Handler(Looper.getMainLooper());
    private static final android.util.LruCache<String,Bitmap> MEMORY=new android.util.LruCache<String,Bitmap>(16*1024){
        @Override protected int sizeOf(String key,Bitmap value){return Math.max(1,value.getByteCount()/1024);}
    };
    private ArtworkCache(){}

    public static boolean isSafeRemoteImage(String input){
        try {
            if(input==null||input.length()>2000)return false;
            URI uri=new URI(input);if(!"https".equalsIgnoreCase(uri.getScheme())||uri.getUserInfo()!=null||uri.getPort()>0)return false;
            String host=uri.getHost();if(host==null)return false;
            host=host.toLowerCase(Locale.ROOT);
            if(host.equals("localhost")||host.endsWith(".local")||host.endsWith(".internal")||host.endsWith(".localhost"))return false;
            // Do not fetch from literal addresses, loopback, link-local or private networks.
            if(host.contains(":")||host.matches("[0-9.]+"))return false;
            return host.contains(".")&&host.length()<=253;
        }catch(Exception ignored){return false;}
    }
    private static String sha(String value){
        try{
            byte[] digest=MessageDigest.getInstance("SHA-256").digest(value.getBytes(java.nio.charset.StandardCharsets.UTF_8));
            StringBuilder s=new StringBuilder();for(byte b:digest)s.append(String.format(Locale.ROOT,"%02x",b&255));return s.toString();
        }catch(Exception e){return Integer.toHexString(value.hashCode());}
    }
    private static File cacheFile(Context context,String url){
        File dir=new File(context.getCacheDir(),"apex_artwork");if(!dir.exists())dir.mkdirs();
        return new File(dir,sha(url)+".jpg");
    }
    private static synchronized void trimDiskCache(File dir){
        File[] files=dir.listFiles(f->f.isFile()&&f.getName().endsWith(".jpg"));
        if(files==null || files.length==0)return;
        java.util.Arrays.sort(files,java.util.Comparator.comparingLong(File::lastModified));
        long bytes=0;
        for(File f:files)bytes+=f.length();
        int count=files.length;
        for(File f:files){
            if(bytes<=40L*1024*1024 && count<=100)break;
            long length=f.length();
            if(f.delete()){bytes-=length;count--;}
        }
    }
    private static Bitmap decode(File file){
        BitmapFactory.Options opts=new BitmapFactory.Options();opts.inJustDecodeBounds=true;
        BitmapFactory.decodeFile(file.getAbsolutePath(),opts);
        if(opts.outWidth<=0||opts.outHeight<=0||opts.outWidth>9000||opts.outHeight>9000)return null;
        opts.inJustDecodeBounds=false;opts.inSampleSize=Math.max(1,Math.max(opts.outWidth,opts.outHeight)/700);
        return BitmapFactory.decodeFile(file.getAbsolutePath(),opts);
    }
    private static boolean isPublicResolvedHost(String hostname) {
        try{
            for(InetAddress a:InetAddress.getAllByName(hostname)){
                if(a.isAnyLocalAddress()||a.isLoopbackAddress()||a.isLinkLocalAddress()||a.isSiteLocalAddress()||a.isMulticastAddress())return false;
            }
            return true;
        }catch(Exception ex){return false;}
    }
    private static Bitmap load(Context context,String thumbnail){
        if(!isSafeRemoteImage(thumbnail))return null;
        synchronized(MEMORY){Bitmap present=MEMORY.get(thumbnail);if(present!=null)return present;}
        File cached=cacheFile(context,thumbnail);
        if(cached.exists()&&cached.length()>0){
            Bitmap bitmap=decode(cached);
            if(bitmap!=null){synchronized(MEMORY){MEMORY.put(thumbnail,bitmap);}return bitmap;}
            cached.delete();
        }
        try{
            URL current=new URL(thumbnail);
            for(int hop=0;hop<=3;hop++){
                if(!isSafeRemoteImage(current.toString())||!isPublicResolvedHost(current.getHost()))return null;
                HttpURLConnection conn=(HttpURLConnection)current.openConnection();
                try{
                    conn.setConnectTimeout(6500);conn.setReadTimeout(6500);conn.setInstanceFollowRedirects(false);
                    conn.setRequestProperty("Accept","image/avif,image/webp,image/jpeg,image/png,*/*");
                    int code=conn.getResponseCode();
                    if(code==301||code==302||code==303||code==307||code==308){
                        String target=conn.getHeaderField("Location");if(target==null)return null;
                        current=new URL(current,target);continue;
                    }
                    if(code!=200||!String.valueOf(conn.getContentType()).toLowerCase(Locale.ROOT).startsWith("image/"))return null;
                    if(conn.getContentLengthLong()>MAX_BYTES)return null;
                    ByteArrayOutputStream out=new ByteArrayOutputStream();byte[] buf=new byte[8192];int n;
                    try(InputStream stream=conn.getInputStream()){
                        while((n=stream.read(buf))!=-1){if(out.size()+n>MAX_BYTES)return null;out.write(buf,0,n);}
                    }
                    byte[] bytes=out.toByteArray();
                    BitmapFactory.Options check=new BitmapFactory.Options();check.inJustDecodeBounds=true;
                    BitmapFactory.decodeByteArray(bytes,0,bytes.length,check);
                    if(check.outWidth<1||check.outHeight<1||check.outWidth>9000||check.outHeight>9000)return null;
                    try(FileOutputStream f=new FileOutputStream(cached)){f.write(bytes);}
                    cached.setLastModified(System.currentTimeMillis());
                    trimDiskCache(cached.getParentFile());
                    Bitmap result=decode(cached);
                    if(result!=null)synchronized(MEMORY){MEMORY.put(thumbnail,result);}
                    return result;
                }finally{conn.disconnect();}
            }
            return null;
        }catch(Exception ex){return null;}
    }
    public static void attach(Context context,ImageView view,String thumbnail){
        view.setImageResource(android.R.drawable.ic_menu_gallery);
        view.setScaleType(ImageView.ScaleType.CENTER_CROP);
        view.setTag(thumbnail);
        if(!isSafeRemoteImage(thumbnail))return;
        Context app=context.getApplicationContext();
        IO.execute(()->{
            Bitmap bitmap=load(app,thumbnail);
            if(bitmap!=null)MAIN.post(()->{if(thumbnail.equals(view.getTag()))view.setImageBitmap(bitmap);});
        });
    }
    /** Try remote artwork, then use a frame from the local media as fallback. */
    public static void attachLocal(Context context,ImageView view,Uri uri,String remote){
        String key=uri.toString()+"|"+remote;
        view.setTag(key);
        view.setImageResource(android.R.drawable.ic_menu_gallery);
        view.setScaleType(ImageView.ScaleType.CENTER_CROP);
        IO.execute(()->{
            Bitmap bitmap=isSafeRemoteImage(remote)?load(context.getApplicationContext(),remote):null;
            if(bitmap==null){
                try{bitmap=context.getContentResolver().loadThumbnail(uri,new Size(240,150),null);}
                catch(Exception ignored){}
            }
            final Bitmap image=bitmap;
            if(image!=null)MAIN.post(()->{if(key.equals(view.getTag()))view.setImageBitmap(image);});
        });
    }
}
