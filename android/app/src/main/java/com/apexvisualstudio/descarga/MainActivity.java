package com.apexvisualstudio.descarga;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.BroadcastReceiver;
import android.content.ClipData;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.text.InputType;
import android.text.TextUtils;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.AdapterView;

import com.yausername.youtubedl_android.YoutubeDL;
import com.yausername.ffmpeg.FFmpeg;

import org.json.JSONArray;
import org.json.JSONObject;

import java.net.URI;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** Apex Descarga Android 1.0.1 UI Pro: native interface; retains 0.5 download engine. */
public final class MainActivity extends Activity {
    private static final String PREF="apex_descarga";
    private static final int SELECT_FOLDER=2114;
    private static final String[] THEMES={"Apex neón","Océano","Violeta","Esmeralda","Coral","Personalizado"};
    private static final int[][] COLORS={{0xFF277AFF,0xFF9B4AFF,0xFF38DAFF},
        {0xFF006BB9,0xFF12B8D8,0xFF5CE4FF},{0xFF7743E4,0xFFE06FFB,0xFFC58CFF},
        {0xFF0E9B7D,0xFF7CC940,0xFF57E5B1},{0xFFDB436F,0xFFFF974F,0xFFFFB6C3},{0xFF277AFF,0xFF9B4AFF,0xFF38DAFF}};
    private static final int BG=0xFF070912, PANEL=0xFF101321, WHITE=0xFFF1F4FF, MUTED=0xFFA8B0CD;
    private int blue,purple,cyan;
    private SharedPreferences prefs;
    private DownloadQueueStore queue;
    private EditText urlInput;
    private Spinner formatQuality, modeSpinner;
    private Button videoBtn,audioBtn,addBtn,updateBtn;
    private TextView engineStatus, previewStatus,queueSummary,folderText;
    private ImageView thumbnail;
    private MediaMetadata analyzedMetadata;
    private String analyzedUrl="";
    private LinearLayout queueRows;
    private String outputFormat="mp4";
    private volatile boolean initialized=false, updating=false;
    private boolean sharedPending=false;
    private final ExecutorService worker=Executors.newSingleThreadExecutor();
    private BroadcastReceiver receiver;
    private String currentFilter="all";

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        prefs=getSharedPreferences(PREF,MODE_PRIVATE);
        queue=new DownloadQueueStore(this);
        int theme=Math.max(0,Math.min(THEMES.length-1,prefs.getInt("theme",0)));
        blue=COLORS[theme][0];purple=COLORS[theme][1];cyan=COLORS[theme][2];
        if(theme==5){
            blue=prefs.getInt("custom_primary",blue);
            purple=prefs.getInt("custom_secondary",purple);
            cyan=prefs.getInt("custom_accent",cyan);
        }
        getWindow().setStatusBarColor(BG);getWindow().setNavigationBarColor(BG);
        draw();
        if(state!=null){urlInput.setText(state.getString("link", ""));}
        else urlInput.setText(prefs.getString("draft_link",""));
        acceptShared(getIntent());
        worker.execute(()->{
            try {
                synchronized(DownloadService.ENGINE_LOCK){
                    YoutubeDL.getInstance().init(getApplicationContext());
                    FFmpeg.getInstance().init(getApplicationContext());
                }
                initialized=true;
                String ver=YoutubeDL.getInstance().versionName(getApplicationContext());
                runOnUiThread(()->{
                    engineStatus.setText("● Motor listo · yt-dlp "+(ver==null?"disponible":ver));
                    if(sharedPending){sharedPending=false;analyze();}
                });
                EngineUpdateJob.schedule(getApplicationContext());
            }catch(Exception ex){runOnUiThread(()->engineStatus.setText("● Motor no disponible: "+shortError(ex)));}
        });
        // Notification permission is optional for Android 13+; downloads still work when denied.
        if(Build.VERSION.SDK_INT>=33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)!=PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},120);
        }
    }
    @Override protected void onStart(){
        super.onStart();
        receiver=new BroadcastReceiver(){@Override public void onReceive(Context c,Intent i){renderQueue();}};
        IntentFilter filter=new IntentFilter(DownloadService.CHANGED);
        if(Build.VERSION.SDK_INT>=33)registerReceiver(receiver,filter,Context.RECEIVER_NOT_EXPORTED);
        else registerReceiver(receiver,filter);
        renderQueue();
        // Resume waiting jobs when the user returns, but never override a paused/cancelled job.
        if(NetworkPolicy.canStart(this)&&queue.pendingCount()>0)DownloadService.enqueue(this);
    }
    @Override protected void onStop(){
        if(receiver!=null){unregisterReceiver(receiver);receiver=null;}
        if(urlInput!=null)prefs.edit().putString("draft_link",urlInput.getText().toString()).apply();
        super.onStop();
    }
    @Override public void onSaveInstanceState(Bundle state){state.putString("link",urlInput.getText().toString());super.onSaveInstanceState(state);}
    @Override protected void onNewIntent(Intent intent){super.onNewIntent(intent);setIntent(intent);acceptShared(intent);}
    private void acceptShared(Intent intent){
        if(intent==null||!Intent.ACTION_SEND.equals(intent.getAction()))return;
        CharSequence raw=intent.getCharSequenceExtra(Intent.EXTRA_TEXT);
        if(raw==null)return;
        Matcher m=Pattern.compile("https?://\\S+",Pattern.CASE_INSENSITIVE).matcher(raw.toString());
        if(m.find()){
            String received=m.group().replaceAll("[)>.,]+$","");
            if(validURL(received)==null)return;
            urlInput.setText(received);
            if(initialized){analyze();}else sharedPending=true;
            toast("Enlace recibido · preparando vista previa");
        }
    }

    private String appearanceToken(){
        return prefs.getInt("theme",0)+":"+prefs.getBoolean("show_logo",true)+":"
            +prefs.getInt("custom_primary",0)+":"+prefs.getInt("custom_secondary",0)+":"+prefs.getInt("custom_accent",0);
    }
    private String lastAppearance="";
    @Override protected void onResume(){
        super.onResume();
        String now=appearanceToken();
        if(!lastAppearance.isEmpty()&&!lastAppearance.equals(now)){
            lastAppearance=now;
            recreate();
            return;
        }
        if(queueRows!=null)renderQueue();
    }
    private void draw(){
        ApexUi ui=new ApexUi(this);
        lastAppearance=appearanceToken();
        LinearLayout root=ui.scaffold(this,"inicio");
        LinearLayout header=row();header.setGravity(Gravity.CENTER_VERTICAL);
        if(prefs.getBoolean("show_logo",true)){
            ImageView logo=new ImageView(this);logo.setImageResource(R.drawable.apex_brand);
            logo.setScaleType(ImageView.ScaleType.FIT_CENTER);
            logo.setBackgroundColor(Color.TRANSPARENT);
            logo.setContentDescription("Logotipo Apex Visual Studio");
            logo.setOnClickListener(v->showLogo());
            header.addView(logo,new LinearLayout.LayoutParams(dp(70),dp(62)));
        }
        LinearLayout headerText=vert();
        headerText.addView(ui.heading("APEX DESCARGA"));
        headerText.addView(ui.text("BY APEX VISUAL STUDIO  ·  UI PRO 1.0.1",10,ui.accent,true));
        header.addView(headerText,new LinearLayout.LayoutParams(0,-2,1));
        root.addView(header);
        engineStatus=ui.chip("● Preparando motor local…",ui.accent);
        LinearLayout.LayoutParams es=lp(-2,-2);es.topMargin=dp(13);root.addView(engineStatus,es);

        LinearLayout content=ui.box(root);
        ui.addAccentLabel(content,"NUEVA DESCARGA");
        ui.addGap(content,5);
        content.addView(ui.text("Descarga lo que importa",20,WHITE,true));
        content.addView(ui.caption("Pega un enlace o compártelo desde otra aplicación."));
        ui.addGap(content,13);
        content.addView(ui.text("ENLACE DEL CONTENIDO",11,MUTED,true));
        urlInput=new EditText(this);
        urlInput.setSingleLine(true);urlInput.setTextColor(WHITE);urlInput.setHintTextColor(MUTED);
        urlInput.setTextSize(13);urlInput.setHint("https://youtube.com/watch?v=...");
        urlInput.setInputType(InputType.TYPE_CLASS_TEXT|InputType.TYPE_TEXT_VARIATION_URI);
        urlInput.setPadding(dp(15),dp(9),dp(15),dp(9));urlInput.setBackground(ui.surface(13,0xFF31435E));
        LinearLayout.LayoutParams inputLp=lp(-1,dp(52));inputLp.topMargin=dp(8);content.addView(urlInput,inputLp);
        urlInput.addTextChangedListener(new android.text.TextWatcher(){
            @Override public void beforeTextChanged(CharSequence s,int start,int count,int after){}
            @Override public void onTextChanged(CharSequence s,int start,int before,int count){
                if(!s.toString().trim().equals(analyzedUrl)){
                    analyzedMetadata=null;analyzedUrl="";
                    if(thumbnail!=null){thumbnail.setVisibility(View.GONE);thumbnail.setTag(null);}
                    if(previewStatus!=null)previewStatus.setText("Analiza un enlace para ver portada, autor y calidades.");
                }
            }
            @Override public void afterTextChanged(android.text.Editable value){}
        });
        LinearLayout linkActions=row();
        Button paste=ui.button("Pegar",false);paste.setOnClickListener(v->paste());
        Button analyze=ui.button("◇  Analizar enlace",true);analyze.setOnClickListener(v->analyze());
        linkActions.addView(paste,weighted(dp(46)));linkActions.addView(analyze,weighted(dp(46)));
        LinearLayout.LayoutParams links=lp(-1,-2);links.topMargin=dp(8);content.addView(linkActions,links);
        ui.addGap(content,12);
        LinearLayout previewCard=vert();previewCard.setPadding(dp(10),dp(10),dp(10),dp(10));
        previewCard.setBackground(ui.surface(14,0));
        content.addView(previewCard);
        thumbnail=new ImageView(this);thumbnail.setScaleType(ImageView.ScaleType.CENTER_CROP);
        thumbnail.setVisibility(View.GONE);thumbnail.setBackground(ui.surface(12,0));thumbnail.setClipToOutline(true);
        previewCard.addView(thumbnail,lp(-1,dp(165)));
        previewStatus=ui.caption("Analiza un enlace para ver portada, autor y calidades.");
        previewStatus.setPadding(dp(5),dp(10),dp(5),dp(6));previewCard.addView(previewStatus);
        ui.addGap(content,16);
        ui.addAccentLabel(content,"FORMATO Y CALIDAD");
        ui.addGap(content,8);
        LinearLayout modes=row();
        videoBtn=ui.button("▣  Video MP4",false);audioBtn=ui.button("♫  Audio MP3",false);
        modes.addView(videoBtn,weighted(dp(48)));modes.addView(audioBtn,weighted(dp(48)));
        videoBtn.setOnClickListener(v->chooseFormat("mp4"));audioBtn.setOnClickListener(v->chooseFormat("mp3"));
        content.addView(modes);
        content.addView(ui.text("Calidad máxima",12,WHITE,true));
        formatQuality=spinner(new String[]{"Mejor disponible","480p","720p HD","1080p Full HD","2160p 4K"});
        formatQuality.setSelection(3);content.addView(formatQuality,lp(-1,dp(50)));
        content.addView(ui.text("Compatibilidad",12,WHITE,true));
        modeSpinner=spinner(new String[]{"MP4 estable","Transporte HLS"});content.addView(modeSpinner,lp(-1,dp(50)));
        CheckBox terms=checkbox("Acepto las condiciones de uso",prefs.getBoolean("accepted_terms",false));
        terms.setOnCheckedChangeListener((b,checked)->prefs.edit().putBoolean("accepted_terms",checked).apply());
        content.addView(terms);
        Button legal=ui.button("Privacidad y condiciones",false);
        legal.setOnClickListener(v->new AlertDialog.Builder(this)
            .setTitle("Privacidad y condiciones").setMessage(PrivacyTerms.TEXT)
            .setPositiveButton("Entendido",null).show());
        content.addView(legal,lp(-1,dp(39)));
        ui.addGap(content,9);
        addBtn=ui.button("↓  AGREGAR A LA COLA",true);
        addBtn.setOnClickListener(v->enqueue());content.addView(addBtn,lp(-1,dp(54)));
        content.addView(ui.text("Solo contenido propio o autorizado · Sin evasión de DRM",10,MUTED,false));

        LinearLayout q=ui.box(root);
        ui.addAccentLabel(q,"ACTIVIDAD");
        q.addView(ui.text("Tus descargas",19,WHITE,true));
        queueSummary=ui.caption("Sin trabajos pendientes");q.addView(queueSummary);
        queueRows=vert();q.addView(queueRows);
        Button openQueue=ui.button("☷  Abrir administrador de descargas",false);
        openQueue.setOnClickListener(v->startActivity(new Intent(this,QueueActivity.class)));
        LinearLayout.LayoutParams oq=lp(-1,dp(48));oq.topMargin=dp(12);q.addView(openQueue,oq);
        chooseFormat(outputFormat);
        renderQueue();
    }
    private void chooseFormat(String format){
        outputFormat=format;boolean mp3="mp3".equals(format);
        if(videoBtn!=null){videoBtn.setAlpha(mp3?.55f:1);audioBtn.setAlpha(mp3?1:.55f);}
        if(formatQuality!=null){formatQuality.setEnabled(!mp3);modeSpinner.setEnabled(!mp3);}
    }
    private static String validURL(String input){
        if(input==null||input.length()>2000)return null;
        try {
            URI uri=new URI(input.trim());
            if(!"https".equalsIgnoreCase(uri.getScheme())&&!"http".equalsIgnoreCase(uri.getScheme()))return null;
            String host=uri.getHost();
            if(host==null||uri.getUserInfo()!=null||host.equalsIgnoreCase("localhost")||host.endsWith(".local")||host.startsWith("127.")||host.equals("0.0.0.0")||host.equals("::1"))return null;
            return uri.toASCIIString();
        }catch(Exception ex){return null;}
    }
    private void enqueue(){
        String url=validURL(urlInput.getText().toString());
        if(url==null){toast("Pega un enlace HTTP(S) válido");return;}
        if(!initialized){toast("Motor no preparado; espera un momento");return;}
        if(!prefs.getBoolean("accepted_terms",false)){
            new AlertDialog.Builder(this).setTitle("Condiciones de uso")
                .setMessage(PrivacyTerms.TEXT).setPositiveButton("Entendido",null).show();
            toast("Acepta primero las condiciones de uso");return;
        }
        long estimate=url.equals(analyzedUrl)&&analyzedMetadata!=null?analyzedMetadata.estimatedBytes:0;
        int limitMB=NetworkPolicy.warnMB(this);
        boolean metered=NetworkPolicy.isMetered(this);
        if(metered&&(estimate<=0||estimate>=limitMB*NetworkPolicy.MB)){
            String detail=estimate>0?NetworkPolicy.displaySize(estimate):"Tamaño desconocido";
            new AlertDialog.Builder(this).setTitle("Uso de datos móviles")
                .setMessage("Estimación: "+detail+". La descarga puede consumir datos de tu tarifa. "
                    +"¿Deseas agregar este archivo a la cola?")
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Agregar",(dialog,which)->addConfirmed(url))
                .show();
            return;
        }
        addConfirmed(url);
    }
    private void addConfirmed(String url){
        String id=queue.add(url,outputFormat,formatQuality.getSelectedItemPosition(),modeSpinner.getSelectedItemPosition()==1);
        if(id==null){toast("La cola admite hasta 15 descargas pendientes");return;}
        if(url.equals(analyzedUrl)&&analyzedMetadata!=null)queue.applyMetadata(url,analyzedMetadata);
        if(NetworkPolicy.canStart(this)){
            DownloadService.enqueue(this);
            toast("Añadido a la cola");
        }else toast("En cola · espera a tener Wi-Fi y pulsa Reanudar");
        renderQueue();
    }
    private void renderQueue(){
        if(queueRows==null)return;
        queueRows.removeAllViews();
        JSONArray jobs=queue.all();int wait=0,run=0,done=0;
        for(int i=0;i<jobs.length();i++){
            JSONObject j=jobs.optJSONObject(i);if(j==null)continue;
            String status=j.optString("status");
            if("waiting".equals(status))wait++;if("running".equals(status))run++;if("done".equals(status))done++;
        }
        queueSummary.setText(run+" activas  ·  "+wait+" pendientes  ·  "+done+" completadas");
        ApexUi ui=new ApexUi(this);int shown=0;
        for(int i=jobs.length()-1;i>=0&&shown<3;i--){
            JSONObject j=jobs.optJSONObject(i);if(j==null)continue;
            String state=j.optString("status", "waiting");
            if("waiting".equals(currentFilter)&&!("waiting".equals(state)||"running".equals(state)||"paused".equals(state)))continue;
            if("failed".equals(currentFilter)&&!"failed".equals(state))continue;
            shown++;
            LinearLayout block=ui.queueCard(j,v->startActivity(new Intent(this,QueueActivity.class)));
            LinearLayout.LayoutParams p=lp(-1,-2);p.topMargin=dp(10);queueRows.addView(block,p);
        }
        if(shown==0){TextView message=text("No hay elementos en esta sección.",12,MUTED,false);
            message.setPadding(dp(8),dp(14),dp(8),dp(14));queueRows.addView(message);}
    }
    private void analyze(){
        String url=validURL(urlInput.getText().toString());
        if(url==null){toast("Introduce un enlace válido");return;}
        if(!initialized){toast("El motor todavía no está preparado");return;}
        analyzedUrl="";analyzedMetadata=null;
        previewStatus.setText("Analizando el video y buscando su portada…");thumbnail.setVisibility(View.GONE);
        worker.execute(()->{
            try{
                MediaMetadata m;
                synchronized(DownloadService.ENGINE_LOCK){m=MediaMetadata.fetch(url);}
                queue.applyMetadata(url,m);
                runOnUiThread(()->{
                    if(!url.equals(validURL(urlInput.getText().toString())))return;
                    analyzedUrl=url;analyzedMetadata=m;
                    previewStatus.setText(m.title+"\n"+m.author+"  ·  "+m.duration
                        +"\n"+m.platform+"\nCalidades: "+m.qualities
                        +"\nTamaño orientativo: "+NetworkPolicy.displaySize(m.estimatedBytes));
                    if(!m.thumbnail.isEmpty()){
                        thumbnail.setVisibility(View.VISIBLE);
                        ArtworkCache.attach(this,thumbnail,m.thumbnail);
                    }else{
                        thumbnail.setVisibility(View.GONE);
                        previewStatus.append("\nEsta plataforma no proporcionó una portada.");
                    }
                    renderQueue();
                });
            }catch(Exception ex){runOnUiThread(()->{
                if(url.equals(validURL(urlInput.getText().toString())))previewStatus.setText("No fue posible analizar este enlace: "+shortError(ex));
            });}
        });
    }
    private static Object call(Object source,String method,Object fallback){
        try{return source.getClass().getMethod(method).invoke(source);}catch(Exception ex){return fallback;}
    }
    private void updateEngine(){
        if(!initialized||updating){toast("El motor no está preparado o ya se está actualizando");return;}
        JSONArray all=queue.all();
        for(int i=0;i<all.length();i++){
            JSONObject item=all.optJSONObject(i);
            if(item!=null&&"running".equals(item.optString("status"))){
                toast("Espera a que termine la descarga antes de actualizar");return;
            }
        }
        if(NetworkPolicy.isMetered(this)){
            new AlertDialog.Builder(this).setTitle("Actualizar mediante datos móviles")
                .setMessage("Esta actualización puede utilizar datos móviles. ¿Continuar?")
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Continuar",(d,w)->performEngineUpdate()).show();
            return;
        }
        performEngineUpdate();
    }
    private void performEngineUpdate(){
        updating=true;updateBtn.setEnabled(false);engineStatus.setText("● Actualizando yt-dlp estable…");
        worker.execute(()->{
            try {
                String version=EngineHealth.updateStable(getApplicationContext());
                runOnUiThread(()->engineStatus.setText("● Actualizado: "+version));
            }catch(Exception ex){runOnUiThread(()->engineStatus.setText("● No se pudo actualizar: "+shortError(ex)));}
            finally{updating=false;runOnUiThread(()->updateBtn.setEnabled(true));}
        });
    }
    private void showCustomColors(){
        LinearLayout fields=vert();fields.setPadding(dp(18),dp(8),dp(18),dp(8));
        EditText[] entries=new EditText[3];
        String[] labels={"Primario","Secundario","Acento"};
        String[] keys={"custom_primary","custom_secondary","custom_accent"};
        int[] defaults={blue,purple,cyan};
        for(int i=0;i<3;i++){
            fields.addView(text(labels[i]+" (#RRGGBB)",12,WHITE,true));
            EditText e=new EditText(this);e.setTextColor(WHITE);e.setSingleLine(true);
            e.setHint("#2876FF");e.setText(String.format(Locale.ROOT,"#%06X",prefs.getInt(keys[i],defaults[i])&0xFFFFFF));
            fields.addView(e);entries[i]=e;
        }
        new AlertDialog.Builder(this).setTitle("Colores a tu gusto")
            .setView(fields).setNegativeButton("Cancelar",(d,w)->d.dismiss())
            .setPositiveButton("Aplicar",(d,w)->{
                int[] selected=new int[3];
                try{
                    for(int i=0;i<3;i++){
                        String value=entries[i].getText().toString().trim();
                        if(!value.matches("#[0-9a-fA-F]{6}"))throw new IllegalArgumentException();
                        selected[i]=Color.parseColor(value);
                    }
                }catch(Exception e){toast("Usa códigos como #2876FF");return;}
                SharedPreferences.Editor editor=prefs.edit();
                for(int i=0;i<3;i++)editor.putInt(keys[i],selected[i]);
                editor.putInt("theme",5).putString("draft_link",urlInput.getText().toString()).apply();
                recreate();
            }).show();
    }
    private void selectFolder(){
        Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION|
            Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION|Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);
        try{startActivityForResult(intent,SELECT_FOLDER);}
        catch(Exception ex){toast("No se encontró el selector de carpetas");}
    }
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent result){
        super.onActivityResult(requestCode,resultCode,result);
        if(requestCode!=SELECT_FOLDER||resultCode!=RESULT_OK||result==null||result.getData()==null)return;
        Uri uri=result.getData();
        try{
            getContentResolver().takePersistableUriPermission(uri,Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            DownloadStorage destination=new DownloadStorage(this);destination.saveTree(uri);
            if(folderText!=null)folderText.setText(destination.destinationLabel());toast("Carpeta personalizada activada");
        }catch(SecurityException ex){toast("Android no otorgó acceso permanente a la carpeta");}
    }
    private void showLogo(){ImageView image=new ImageView(this);image.setImageResource(R.drawable.apex_brand);image.setScaleType(ImageView.ScaleType.FIT_CENTER);
        new AlertDialog.Builder(this).setTitle("Apex Visual Studio").setView(image).setPositiveButton("Cerrar",(d,w)->d.dismiss()).show();}
    private void paste(){
        android.content.ClipboardManager clipboard=(android.content.ClipboardManager)getSystemService(CLIPBOARD_SERVICE);
        if(clipboard!=null&&clipboard.hasPrimaryClip()){
            ClipData data=clipboard.getPrimaryClip();if(data!=null&&data.getItemCount()>0){
                CharSequence value=data.getItemAt(0).coerceToText(this);urlInput.setText(value==null?"":value.toString());
            }
        } else toast("Portapapeles vacío");
    }
    private static String shortError(Exception ex){String s=String.valueOf(ex.getMessage());return s.length()>130?s.substring(0,130)+"…":s;}
    private void toast(String s){android.widget.Toast.makeText(this,s,android.widget.Toast.LENGTH_SHORT).show();}
    private int dp(int p){return Math.round(p*getResources().getDisplayMetrics().density);}
    private LinearLayout vert(){LinearLayout v=new LinearLayout(this);v.setOrientation(LinearLayout.VERTICAL);return v;}
    private LinearLayout row(){LinearLayout r=new LinearLayout(this);r.setOrientation(LinearLayout.HORIZONTAL);r.setGravity(Gravity.CENTER_VERTICAL);return r;}
    private LinearLayout.LayoutParams lp(int w,int h){return new LinearLayout.LayoutParams(w,h);}
    private LinearLayout.LayoutParams weighted(int h){LinearLayout.LayoutParams p=new LinearLayout.LayoutParams(0,h,1);p.setMargins(dp(2),0,dp(2),0);return p;}
    private GradientDrawable panel(int radius,int stroke){GradientDrawable gd=new GradientDrawable(GradientDrawable.Orientation.TL_BR,new int[]{0xFF141B2E,0xFF0D1220});
        gd.setCornerRadius(dp(radius));gd.setStroke(dp(1),stroke);return gd;}
    private LinearLayout card(){LinearLayout c=vert();c.setPadding(dp(16),dp(17),dp(16),dp(17));c.setBackground(panel(21,0xFF2E3C59));
        LinearLayout.LayoutParams p=lp(-1,-2);p.topMargin=dp(17);c.setLayoutParams(p);return c;}
    private TextView text(String value,int size,int color,boolean bold){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);
        t.setPadding(0,dp(5),0,dp(5));if(bold)t.setTypeface(Typeface.DEFAULT,Typeface.BOLD);return t;}
    private View section(String n,String name){LinearLayout r=row();TextView badge=text(n,12,cyan,true);badge.setBackground(panel(9,blue));badge.setPadding(dp(9),dp(7),dp(9),dp(7));r.addView(badge);
        TextView title=text("  "+name,16,WHITE,true);r.addView(title);return r;}
    private Button button(String caption,boolean prominent){Button b=new Button(this);b.setText(caption);b.setTextSize(prominent?14:12);b.setAllCaps(false);
        b.setTextColor(WHITE);b.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        if(prominent){GradientDrawable g=new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,new int[]{blue,purple});g.setCornerRadius(dp(13));b.setBackground(g);}
        else b.setBackground(panel(13,0xFF34466B));return b;}
    private Spinner spinner(String[] options){Spinner s=new Spinner(this);ArrayAdapter<String> a=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,options);
        s.setAdapter(a);s.setBackground(panel(13,0xFF374366));return s;}
    private CheckBox checkbox(String label,boolean checked){CheckBox box=new CheckBox(this);box.setText(label);box.setTextColor(WHITE);box.setTextSize(12);
        box.setButtonTintList(android.content.res.ColorStateList.valueOf(cyan));box.setChecked(checked);return box;}
    @Override protected void onDestroy(){worker.shutdown();super.onDestroy();}
}
