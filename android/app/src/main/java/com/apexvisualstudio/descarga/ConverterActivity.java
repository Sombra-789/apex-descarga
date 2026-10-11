package com.apexvisualstudio.descarga;

import android.app.Activity;
import android.content.Intent;
import android.content.ActivityNotFoundException;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.media.MediaExtractor;
import android.media.MediaFormat;
import android.media.MediaMuxer;
import android.media.MediaMetadataRetriever;
import android.media.MediaCodec;
import android.net.Uri;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.text.InputType;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.ByteBuffer;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Native Android lossless MP4 trim and AAC->M4A extraction, no arbitrary shell commands. */
public final class ConverterActivity extends Activity {
    private static final int PICK=52;
    private final ExecutorService executor=Executors.newSingleThreadExecutor();
    private Uri input;
    private TextView message;
    private Button convertButton;
    private EditText begin,end;
    private Spinner action;
    private int dp(int v){return Math.round(v*getResources().getDisplayMetrics().density);}
    private TextView t(String str,int size){TextView v=new TextView(this);v.setText(str);v.setTextSize(size);v.setTextColor(Color.WHITE);v.setPadding(0,dp(8),0,dp(8));return v;}
    private Button button(String str){Button b=new Button(this);b.setText(str);b.setTextColor(Color.WHITE);b.setAllCaps(false);
        ApexUi style=new ApexUi(this);b.setBackground(style.surface(13,0xFF304166));return b;}
    @Override public void onCreate(Bundle state){super.onCreate(state);getWindow().setStatusBarColor(0xFF070912);
        ApexUi ui=new ApexUi(this);
        LinearLayout root=ui.scaffold(this,"biblioteca");
        TextView title=t("Conversor multimedia",23);title.setTypeface(Typeface.DEFAULT,Typeface.BOLD);root.addView(title);
        root.addView(t("Procesa tus propios archivos sin subirlos a servidores.",12));
        root.addView(t("En esta versión: extraer audio AAC como M4A o recortar MP4 sin recodificar.",12));
        Button pick=button("Seleccionar archivo del dispositivo");pick.setOnClickListener(v->choose());root.addView(pick,new LinearLayout.LayoutParams(-1,dp(52)));
        message=t("Ningún archivo elegido",13);root.addView(message);
        action=new Spinner(this);action.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,
            new String[]{"Extraer audio a M4A","Recortar MP4 (sin recodificar)"}));root.addView(action);
        root.addView(t("Inicio en segundos (0 = principio)",12));begin=new EditText(this);begin.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_DECIMAL);
        begin.setText("0");begin.setTextColor(Color.WHITE);root.addView(begin);
        root.addView(t("Fin en segundos (vacío = hasta el final)",12));end=new EditText(this);end.setInputType(InputType.TYPE_CLASS_NUMBER|InputType.TYPE_NUMBER_FLAG_DECIMAL);
        end.setHint("Sin límite");end.setTextColor(Color.WHITE);root.addView(end);
        convertButton=button("Procesar archivo");convertButton.setOnClickListener(v->convert());root.addView(convertButton,new LinearLayout.LayoutParams(-1,dp(54)));
        root.addView(t("Nota: el recorte se ajusta a fotogramas clave. La conversión MP3 de archivos locales queda para una versión posterior; las descargas a MP3 siguen disponibles.",11));
    }
    private void choose(){Intent i=new Intent(Intent.ACTION_OPEN_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("*/*");
        i.putExtra(Intent.EXTRA_MIME_TYPES,new String[]{"video/mp4","audio/mp4"});
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try{startActivityForResult(i,PICK);}catch(ActivityNotFoundException e){toast("No hay selector de archivos");}}
    @Override protected void onActivityResult(int code,int result,Intent data){super.onActivityResult(code,result,data);
        if(code==PICK&&result==RESULT_OK&&data!=null){input=data.getData();message.setText("Archivo seleccionado · "+input);}}
    private void convert(){
        if(input==null){toast("Selecciona un archivo primero");return;}
        double start,endSec;
        try{start=Double.parseDouble(begin.getText().toString());endSec=end.getText().length()==0?-1:Double.parseDouble(end.getText().toString());
            if(start<0||endSec>=0&&endSec<=start)throw new Exception();
        }catch(Exception ex){toast("Introduce segundos válidos");return;}
        boolean audio=action.getSelectedItemPosition()==0;
        convertButton.setEnabled(false);message.setText("Procesando archivo local…");
        Uri source=input;
        executor.execute(()->{
            File folder=null;
            try{
                DownloadStorage storage=new DownloadStorage(this);folder=storage.createJobDirectory();
                File output=new File(folder,"Apex_"+System.currentTimeMillis()+(audio?".m4a":".mp4"));
                remux(source,output,start,endSec,audio);
                Uri uri=storage.publish(output);
                new LibraryStore(this).add(output.getName(),uri,audio?"audio/mp4":"video/mp4");
                runOnUiThread(()->{message.setText("✓ Archivo guardado en Descargas / Apex Descarga");toast("Conversión completada");});
            }catch(Exception ex){String messageText=ex.getMessage();runOnUiThread(()->message.setText("No fue posible procesarlo: "+messageText));}
            finally{DownloadStorage.cleanup(folder);runOnUiThread(()->convertButton.setEnabled(true));}
        });
    }
    private void remux(Uri uri,File destination,double start,double until,boolean audioOnly) throws Exception{
        MediaExtractor extractor=new MediaExtractor();MediaMuxer muxer=null;
        try(ParcelFileDescriptor pfd=getContentResolver().openFileDescriptor(uri,"r")){
            if(pfd==null)throw new Exception("El archivo no se puede abrir");
            extractor.setDataSource(pfd.getFileDescriptor());
            muxer=new MediaMuxer(destination.getAbsolutePath(),MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
            if(!audioOnly){
                MediaMetadataRetriever metadata=new MediaMetadataRetriever();
                try{
                    metadata.setDataSource(pfd.getFileDescriptor());
                    String rotation=metadata.extractMetadata(MediaMetadataRetriever.METADATA_KEY_VIDEO_ROTATION);
                    if(rotation!=null)muxer.setOrientationHint(Integer.parseInt(rotation));
                }catch(Exception ignored){}finally{metadata.release();}
            }
            int[] mapping=new int[extractor.getTrackCount()];java.util.Arrays.fill(mapping,-1);
            int selected=0;
            for(int i=0;i<extractor.getTrackCount();i++){
                MediaFormat format=extractor.getTrackFormat(i);
                String mime=format.getString(MediaFormat.KEY_MIME);
                if(mime==null)continue;
                boolean isAAC=mime.equals("audio/mp4a-latm");
                boolean compatible=mime.startsWith("video/MP4V")||mime.startsWith("video/avc")||mime.startsWith("video/hevc")||mime.startsWith("video/av01")||isAAC;
                if(audioOnly&&!isAAC)continue;
                if(!audioOnly&&!compatible)continue;
                mapping[i]=muxer.addTrack(format);extractor.selectTrack(i);selected++;
            }
            if(selected==0)throw new Exception(audioOnly?"El archivo no contiene audio AAC compatible con M4A":"No se encontraron pistas MP4 compatibles");
            muxer.start();
            long from=(long)(start*1_000_000),to=until<0?Long.MAX_VALUE:(long)(until*1_000_000);
            extractor.seekTo(from,MediaExtractor.SEEK_TO_PREVIOUS_SYNC);
            ByteBuffer buffer=ByteBuffer.allocateDirect(4*1024*1024);
            MediaCodec.BufferInfo info=new MediaCodec.BufferInfo();
            int samples=0;
            for(;;){
                int track=extractor.getSampleTrackIndex();if(track<0)break;
                int outputTrack=mapping[track];long time=extractor.getSampleTime();
                if(time>to)break;
                if(outputTrack>=0&&time>=from){
                    buffer.clear();int len=extractor.readSampleData(buffer,0);
                    if(len<0)break;
                    info.offset=0;info.size=len;info.presentationTimeUs=Math.max(0,time-from);info.flags=extractor.getSampleFlags();
                    muxer.writeSampleData(outputTrack,buffer,info);samples++;
                }
                if(!extractor.advance())break;
            }
            if(samples==0)throw new Exception("No hay muestras en ese intervalo");
        }finally{
            extractor.release();
            if(muxer!=null){try{muxer.stop();}catch(Exception ignored){}muxer.release();}
        }
    }
    private void toast(String txt){Toast.makeText(this,txt,Toast.LENGTH_SHORT).show();}
    @Override protected void onDestroy(){executor.shutdown();super.onDestroy();}
}
