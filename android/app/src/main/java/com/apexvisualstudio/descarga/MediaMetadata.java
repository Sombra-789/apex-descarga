package com.apexvisualstudio.descarga;

import com.yausername.youtubedl_android.YoutubeDL;
import org.json.JSONObject;
import java.lang.reflect.Method;
import java.net.URI;
import java.util.Locale;
import java.util.TreeSet;

/** Metadata associated with a specific source URL. Does not request cookies or authentication. */
public final class MediaMetadata {
    public final String title, author, thumbnail, platform, duration, qualities;
    public final long durationSeconds, estimatedBytes;

    public MediaMetadata(String title, String author, String thumbnail, String platform, String duration, String qualities, long seconds, long bytes) {
        this.title=bound(title, 160, "Contenido");
        this.author=bound(author, 90, "Autor desconocido");
        this.thumbnail=bound(thumbnail, 2000, "");
        this.platform=bound(platform, 90, "Sitio web");
        this.duration=duration;
        this.qualities=qualities;
        this.durationSeconds=seconds;
        this.estimatedBytes=Math.max(0,bytes);
    }
    private static String bound(String s,int max,String fallback) {
        if(s==null||s.trim().isEmpty()||"null".equalsIgnoreCase(s.trim()))return fallback;
        String out=s.trim().replaceAll("[\\p{Cntrl}&&[^\\n]]", " ");
        return out.length()>max?out.substring(0,max):out;
    }
    private static Object get(Object obj,String... names){
        if(obj==null)return null;
        for(String name:names){try{Method m=obj.getClass().getMethod(name);Object v=m.invoke(obj);if(v!=null)return v;}catch(Exception ignored){}}
        return null;
    }
    private static String str(Object v){return v==null?"":String.valueOf(v);}
    public static String urlThumbnail(String link) {
        try{
            URI u=new URI(link);String host=u.getHost();if(host==null)return "";
            host=host.toLowerCase(Locale.ROOT);
            String id="";
            if(host.equals("youtu.be")||host.equals("www.youtu.be"))id=u.getPath().replaceFirst("^/","").split("/")[0];
            else if(host.equals("youtube.com")||host.equals("www.youtube.com")||host.equals("m.youtube.com")){
                if(u.getPath().startsWith("/shorts/"))id=u.getPath().substring(8).split("/")[0];
                else if("/watch".equals(u.getPath()) && u.getRawQuery()!=null){
                    for(String arg:u.getRawQuery().split("&"))if(arg.startsWith("v=")){id=arg.substring(2);break;}
                }
            }
            return id.matches("[a-zA-Z0-9_-]{11}")?"https://i.ytimg.com/vi/"+id+"/hqdefault.jpg":"";
        }catch(Exception ignored){return "";}
    }
    private static String safeThumbnail(String raw,String link){
        if(ArtworkCache.isSafeRemoteImage(raw))return raw;
        return urlThumbnail(link);
    }
    private static String resolveThumbnail(Object info){
        String direct=str(get(info,"getThumbnail","getThumbnailUrl","getThumbnailURL"));
        if(direct.startsWith("https://"))return direct;
        Object thumbs=get(info,"getThumbnails");
        if(thumbs instanceof Iterable){
            String selected="";
            for(Object thumb:(Iterable<?>)thumbs){
                String candidate=thumb instanceof JSONObject?((JSONObject)thumb).optString("url"):str(get(thumb,"getUrl"));
                if(candidate.startsWith("https://"))selected=candidate;
            }
            return selected;
        }
        return "";
    }
    public static MediaMetadata fetch(String url) throws Exception {
        Object info=YoutubeDL.getInstance().getInfo(url);
        String title=str(get(info,"getTitle"));
        String author=str(get(info,"getUploader","getArtist","getChannel","getCreator"));
        Object duration=get(info,"getDuration");
        long seconds=duration instanceof Number?Math.max(0,((Number)duration).longValue()):0;
        String durationText=seconds>0?String.format(Locale.ROOT,"%d:%02d",seconds/60,seconds%60):"Duración no disponible";
        String domain;
        try{domain=new URI(url).getHost();}catch(Exception ex){domain="Sitio web";}
        TreeSet<Integer> res=new TreeSet<>();
        long bestBytes=0;
        Object formats=get(info,"getFormats");
        if(formats instanceof Iterable){
            for(Object f:(Iterable<?>)formats){
                Object h=get(f,"getHeight");
                if(h instanceof Number){int height=((Number)h).intValue();if(height>0&&height<=4320)res.add(height);}
                Object size=get(f,"getFilesize","getFilesizeApprox","getFileSize","getFileSizeApprox");
                if(size instanceof Number)bestBytes=Math.max(bestBytes,((Number)size).longValue());
            }
        }
        StringBuilder quality=new StringBuilder();
        for(Integer h:res.descendingSet()){if(quality.length()>0)quality.append(" · ");quality.append(h).append('p');if(quality.length()>75)break;}
        if(quality.length()==0)quality.append("Mejor disponible");
        return new MediaMetadata(title,author,safeThumbnail(resolveThumbnail(info),url),domain,durationText,quality.toString(),seconds,bestBytes);
    }
}
