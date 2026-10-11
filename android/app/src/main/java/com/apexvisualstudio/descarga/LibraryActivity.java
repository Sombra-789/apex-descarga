package com.apexvisualstudio.descarga;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONArray;
import org.json.JSONObject;
import java.text.DateFormat;
import java.util.Date;
import java.util.Locale;

/** Android-scoped library; indexes only media published by Apex, no broad storage access. */
public final class LibraryActivity extends Activity {
    private LibraryStore library;
    private ApexUi ui;
    private LinearLayout list;
    private EditText search;
    private String currentFilter="all";
    private String oldPalette="";
    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        ui=new ApexUi(this);library=new LibraryStore(this);oldPalette=ThemeIdentity.token(this);
        getWindow().setStatusBarColor(ApexUi.BG);getWindow().setNavigationBarColor(ApexUi.BG);
        LinearLayout root=ui.scaffold(this,"biblioteca");
        root.addView(ui.heading("Tu biblioteca"));
        TextView caption=ui.text("Tus archivos guardados desde Apex Descarga",12,ApexUi.MUTED,false);
        LinearLayout.LayoutParams cp=ui.lp(-1,-2);cp.topMargin=ui.dp(8);root.addView(caption,cp);
        search=new EditText(this);search.setTextSize(13);search.setSingleLine(true);
        search.setTextColor(ApexUi.WHITE);search.setHintTextColor(ApexUi.MUTED);search.setHint("Buscar un archivo…");
        search.setPadding(ui.dp(13),ui.dp(7),ui.dp(13),ui.dp(7));search.setBackground(ui.surface(13,0xFF304166));
        LinearLayout.LayoutParams sp=ui.lp(-1,ui.dp(51));sp.topMargin=ui.dp(18);root.addView(search,sp);
        search.addTextChangedListener(new TextWatcher(){@Override public void beforeTextChanged(CharSequence s,int st,int count,int aft){}
            @Override public void onTextChanged(CharSequence s,int start,int before,int count){draw();}
            @Override public void afterTextChanged(Editable e){}
        });
        LinearLayout tabs=ui.row();LinearLayout.LayoutParams tp=ui.lp(-1,-2);tp.topMargin=ui.dp(11);root.addView(tabs,tp);
        for(String[] type:new String[][]{{"Todos","all"},{"Videos","video"},{"Audios","audio"}}){
            Button b=ui.button(type[0],false);b.setOnClickListener(v->{currentFilter=type[1];draw();});
            tabs.addView(b,new LinearLayout.LayoutParams(0,ui.dp(42),1));
        }
        list=ui.vert();LinearLayout.LayoutParams l=ui.lp(-1,-2);l.topMargin=ui.dp(11);root.addView(list,l);
        draw();
    }
    @Override protected void onResume(){
        super.onResume();
        if(!oldPalette.equals(ThemeIdentity.token(this))){recreate();return;}
        if(list!=null)draw();
    }
    private void draw(){
        if(list==null)return;
        list.removeAllViews();JSONArray entries=library.all();int shown=0;
        String query=search.getText().toString().trim().toLowerCase(Locale.ROOT);
        for(int i=0;i<entries.length();i++){
            JSONObject obj=entries.optJSONObject(i);if(obj==null)continue;
            String mime=obj.optString("mime","video/mp4"),name=obj.optString("name","Archivo");
            boolean audio=mime.startsWith("audio/");
            if(currentFilter.equals("video")&&audio||currentFilter.equals("audio")&&!audio)continue;
            String title=obj.optString("title",name);
            if(!(title+" "+name+" "+obj.optString("author","")).toLowerCase(Locale.ROOT).contains(query))continue;
            shown++;
            Uri uri=Uri.parse(obj.optString("uri"));
            LinearLayout card=ui.card();
            LinearLayout header=ui.row();
            ImageView image=new ImageView(this);image.setBackground(ui.surface(12,0));image.setClipToOutline(true);
            ArtworkCache.attachLocal(this,image,uri,obj.optString("thumbnail",""));
            header.addView(image,new LinearLayout.LayoutParams(ui.dp(88),ui.dp(79)));
            LinearLayout details=ui.vert();details.setPadding(ui.dp(12),0,0,0);
            TextView nameText=ui.text(title,13,ApexUi.WHITE,true);nameText.setMaxLines(2);
            nameText.setEllipsize(android.text.TextUtils.TruncateAt.END);details.addView(nameText);
            String subtitle=obj.optString("author","");if(subtitle.isEmpty())subtitle=obj.optString("platform","");
            details.addView(ui.text(subtitle,11,ApexUi.MUTED,false));
            details.addView(ui.chip(audio?"MP3 / AUDIO":"VIDEO",ui.accent));
            details.addView(ui.text(DateFormat.getDateTimeInstance(DateFormat.SHORT,DateFormat.SHORT).format(new Date(obj.optLong("when"))),10,ApexUi.MUTED,false));
            header.addView(details,new LinearLayout.LayoutParams(0,-2,1));card.addView(header);
            LinearLayout buttons=ui.row();LinearLayout.LayoutParams bp=ui.lp(-1,-2);bp.topMargin=ui.dp(10);
            Button open=ui.button("Abrir",false);open.setOnClickListener(v->open(uri,mime));
            Button share=ui.button("Compartir",false);share.setOnClickListener(v->share(uri,mime));
            Button delete=ui.button("Eliminar",false);delete.setOnClickListener(v->new AlertDialog.Builder(this)
                .setTitle("Eliminar archivo")
                .setMessage("¿Eliminar este archivo y quitarlo de la biblioteca? No se puede deshacer.")
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Eliminar",(d,w)->{
                    try{if(getContentResolver().delete(uri,null,null)>0){library.remove(uri.toString());draw();}
                        else toast("Android no confirmó la eliminación del archivo");}
                    catch(Exception ex){toast("Android no permitió eliminar el archivo");}
                }).show());
            for(Button b:new Button[]{open,share,delete})buttons.addView(b,new LinearLayout.LayoutParams(0,ui.dp(43),1));
            card.addView(buttons,bp);
            LinearLayout.LayoutParams p=ui.lp(-1,-2);p.bottomMargin=ui.dp(12);list.addView(card,p);
        }
        if(shown==0){TextView empty=ui.text("No encontramos archivos aquí. Las descargas antiguas de Apex 0.2 pueden no estar indexadas.",13,ApexUi.MUTED,false);
            empty.setPadding(ui.dp(9),ui.dp(28),ui.dp(9),ui.dp(28));list.addView(empty);}
    }
    private void open(Uri uri,String mime){
        try{Intent it=new Intent(Intent.ACTION_VIEW);it.setDataAndType(uri,mime);
            it.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);startActivity(it);}
        catch(ActivityNotFoundException ex){toast("No tienes una aplicación para abrir este archivo");}
        catch(Exception ex){toast("No fue posible abrir este archivo");}
    }
    private void share(Uri uri,String mime){
        try{Intent it=new Intent(Intent.ACTION_SEND);it.setType(mime);it.putExtra(Intent.EXTRA_STREAM,uri);
            it.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);startActivity(Intent.createChooser(it,"Compartir archivo"));}
        catch(Exception ex){toast("No fue posible compartir este archivo");}
    }
    private void toast(String s){Toast.makeText(this,s,Toast.LENGTH_SHORT).show();}
}
