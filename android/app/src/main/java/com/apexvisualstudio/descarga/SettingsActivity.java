package com.apexvisualstudio.descarga;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.view.Gravity;
import android.widget.ArrayAdapter;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import com.yausername.youtubedl_android.YoutubeDL;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/** UI Pro settings: preserves all 0.5 preferences and engine behavior. */
public final class SettingsActivity extends Activity {
    private static final int SELECT_FOLDER=2114;
    private final ExecutorService worker=Executors.newSingleThreadExecutor();
    private SharedPreferences prefs;
    private ApexUi ui;
    private TextView folderLabel, engineLabel, engineIssueLabel;
    private Button engineButton;
    private volatile boolean updating=false;
    private final String[] themes={"Apex neón","Océano","Violeta","Esmeralda","Coral","Personalizado"};

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        prefs=getSharedPreferences("apex_descarga",MODE_PRIVATE);
        ui=new ApexUi(this);
        LinearLayout root=ui.scaffold(this,"ajustes");
        root.addView(ui.heading("Ajustes"));
        ui.addGap(root,5);
        root.addView(ui.caption("Tu experiencia, a tu manera"));

        LinearLayout appearance=ui.box(root);
        ui.addAccentLabel(appearance,"APARIENCIA");
        ui.addGap(appearance,5);
        appearance.addView(ui.text("Personaliza Apex",18,ApexUi.WHITE,true));
        appearance.addView(ui.caption("Selecciona una paleta o define tus propios colores."));
        ui.addGap(appearance,9);
        LinearLayout swatches=ui.row();
        int[] colors={0xFF3985FF,0xFF12B8D8,0xFF7743E4,0xFF0E9B7D,0xFFFF974F};
        for(int i=0;i<colors.length;i++){
            final int index=i;
            TextView dot=ui.text("●",31,colors[i],false);
            dot.setGravity(Gravity.CENTER);
            swatches.addView(dot,new LinearLayout.LayoutParams(0,ui.dp(45),1));
            dot.setContentDescription("Elegir paleta "+themes[i]);
            dot.setOnClickListener(v->{prefs.edit().putInt("theme",index).apply();recreate();});
        }
        appearance.addView(swatches);
        Spinner theme=new Spinner(this);
        ArrayAdapter<String> choices=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,themes);
        theme.setAdapter(choices);
        theme.setBackground(ui.surface(12,0xFF354767));
        int selection=Math.max(0,Math.min(5,prefs.getInt("theme",0)));
        theme.setSelection(selection);
        theme.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){
            @Override public void onNothingSelected(AdapterView<?> parent){}
            @Override public void onItemSelected(AdapterView<?> parent,View view,int pos,long id){
                if(pos==prefs.getInt("theme",0))return;
                if(pos==5){editColors();return;}
                prefs.edit().putInt("theme",pos).apply();recreate();
            }
        });
        appearance.addView(theme,new LinearLayout.LayoutParams(-1,ui.dp(48)));
        Button custom=ui.button("Editar colores HEX personalizados",false);
        custom.setOnClickListener(v->editColors());
        appearance.addView(custom,new LinearLayout.LayoutParams(-1,ui.dp(45)));
        CheckBox logo=checkbox("Mostrar logotipo",prefs.getBoolean("show_logo",true));
        logo.setOnCheckedChangeListener((v,checked)->prefs.edit().putBoolean("show_logo",checked).apply());
        appearance.addView(logo);
        appearance.addView(ui.caption("El logotipo no tiene bordes; puedes ocultarlo en Inicio."));

        LinearLayout network=ui.box(root);
        ui.addAccentLabel(network,"DATOS Y CONECTIVIDAD");
        CheckBox wifi=checkbox("Descargar solo mediante Wi-Fi",NetworkPolicy.wifiOnly(this));
        wifi.setOnCheckedChangeListener((v,on)->{
            prefs.edit().putBoolean(NetworkPolicy.WIFI_ONLY,on).apply();
            if(on)toast("Las descargas pendientes esperarán Wi-Fi");
        });
        network.addView(wifi);
        network.addView(ui.caption("Si pierdes Wi-Fi, Apex detendrá la transferencia activa para proteger tus datos."));
        ui.addGap(network,7);
        network.addView(ui.text("Aviso de consumo en datos móviles",13,ApexUi.WHITE,true));
        Spinner limit=new Spinner(this);
        limit.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,
            new String[]{"50 MB","100 MB","250 MB","500 MB"}));
        limit.setBackground(ui.surface(12,0xFF354767));
        int[] sizes={50,100,250,500};int curr=NetworkPolicy.warnMB(this),idx=0;
        for(int i=0;i<sizes.length;i++)if(sizes[i]==curr)idx=i;
        limit.setSelection(idx);
        limit.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener(){
            @Override public void onNothingSelected(AdapterView<?> p){}
            @Override public void onItemSelected(AdapterView<?> p,View v,int pos,long id){
                prefs.edit().putInt(NetworkPolicy.WARN_MB,sizes[pos]).apply();
            }
        });
        network.addView(limit,new LinearLayout.LayoutParams(-1,ui.dp(48)));

        LinearLayout folder=ui.box(root);
        ui.addAccentLabel(folder,"ALMACENAMIENTO");
        folder.addView(ui.text("Carpeta de destino",16,ApexUi.WHITE,true));
        DownloadStorage storage=new DownloadStorage(this);
        folderLabel=ui.caption(storage.destinationLabel());
        folder.addView(folderLabel);
        LinearLayout actions=ui.row();
        Button change=ui.button("Cambiar carpeta",false);
        change.setOnClickListener(v->openFolderPicker());
        Button reset=ui.button("Predeterminada",false);
        reset.setOnClickListener(v->{storage.resetTree();folderLabel.setText(storage.destinationLabel());toast("Carpeta predeterminada activada");});
        actions.addView(change,new LinearLayout.LayoutParams(0,ui.dp(45),1));
        actions.addView(reset,new LinearLayout.LayoutParams(0,ui.dp(45),1));
        folder.addView(actions);

        LinearLayout engine=ui.box(root);
        ui.addAccentLabel(engine,"MOTOR MULTIMEDIA");
        engine.addView(ui.text("yt-dlp",18,ApexUi.WHITE,true));
        engineLabel=ui.caption("Consultando versión instalada…");engine.addView(engineLabel);
        CheckBox automatic=checkbox("Buscar actualizaciones con Wi-Fi",prefs.getBoolean("auto_engine_update",true));
        automatic.setOnCheckedChangeListener((v,on)->{
            prefs.edit().putBoolean("auto_engine_update",on).apply();EngineUpdateJob.schedule(this);
        });
        engine.addView(automatic);
        engine.addView(ui.caption("Android programa una revisión estable aproximadamente cada siete días. No modifica el APK."));
        ui.addGap(engine,7);
        engineButton=ui.button("↻  Actualizar yt-dlp",true);
        engineButton.setOnClickListener(v->updateEngine());
        engine.addView(engineButton,new LinearLayout.LayoutParams(-1,ui.dp(49)));
        String issue=prefs.getString("engine_update_issue","");
        engineIssueLabel=ui.text("",11,0xFFFFB6C3,false);
        engine.addView(engineIssueLabel);
        showEngineIssue(issue);
        engine.addView(ui.caption("Las actualizaciones utilizan el canal estable del motor, sin descargar APK externos."));
        worker.execute(()->{
            try{
                synchronized(DownloadService.ENGINE_LOCK){YoutubeDL.getInstance().init(getApplicationContext());}
                String version=EngineVersion.normalize(YoutubeDL.getInstance().versionName(getApplicationContext()));
                runOnUiThread(()->engineLabel.setText("Versión instalada: "+(version.isEmpty()?"No verificable":version)));
            }catch(Exception ex){runOnUiThread(()->engineLabel.setText("No disponible: "+brief(ex)));}
        });
        ui.addGap(root,15);
        root.addView(ui.caption("APEX DESCARGA · ANDROID UI PRO 1.0.1 · BY APEX VISUAL STUDIO"));
    }
    private CheckBox checkbox(String text,boolean checked){
        CheckBox c=new CheckBox(this);c.setText(text);c.setTextColor(ApexUi.WHITE);c.setTextSize(13);
        c.setButtonTintList(ColorStateList.valueOf(ui.accent));c.setChecked(checked);return c;
    }
    private void editColors(){
        LinearLayout wrap=ui.vert();wrap.setPadding(ui.dp(20),ui.dp(10),ui.dp(20),ui.dp(8));
        EditText[] values=new EditText[3];
        String[] keys={"custom_primary","custom_secondary","custom_accent"};
        String[] names={"Primario","Secundario","Acento"};
        int[] defaults={ui.primary,ui.secondary,ui.accent};
        for(int i=0;i<3;i++){
            wrap.addView(ui.text(names[i],12,ApexUi.WHITE,true));
            EditText input=new EditText(this);input.setSingleLine(true);input.setTextColor(ApexUi.WHITE);
            input.setText(String.format(Locale.ROOT,"#%06X",prefs.getInt(keys[i],defaults[i])&0xFFFFFF));
            wrap.addView(input);values[i]=input;
        }
        new AlertDialog.Builder(this).setTitle("Colores personalizados")
            .setView(wrap).setNegativeButton("Cancelar",null)
            .setPositiveButton("Aplicar",(dialog,which)->{
                int[] newColors=new int[3];
                for(int i=0;i<3;i++){
                    String h=values[i].getText().toString().trim();
                    if(!h.matches("#[0-9a-fA-F]{6}")){toast("Formato válido: #3985FF");return;}
                    newColors[i]=Color.parseColor(h);
                }
                SharedPreferences.Editor edit=prefs.edit();
                for(int i=0;i<3;i++)edit.putInt(keys[i],newColors[i]);
                edit.putInt("theme",5).apply();recreate();
            }).show();
    }
    private void openFolderPicker(){
        Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION|
            Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION|Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);
        try{startActivityForResult(intent,SELECT_FOLDER);}catch(Exception ex){toast("No se pudo abrir el selector");}
    }
    @Override protected void onActivityResult(int requestCode,int resultCode,Intent result){
        super.onActivityResult(requestCode,resultCode,result);
        if(requestCode!=SELECT_FOLDER||resultCode!=RESULT_OK||result==null||result.getData()==null)return;
        Uri uri=result.getData();
        try{
            getContentResolver().takePersistableUriPermission(uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION|Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
            DownloadStorage storage=new DownloadStorage(this);
            storage.saveTree(uri);folderLabel.setText(storage.destinationLabel());toast("Carpeta guardada");
        }catch(Exception ex){toast("Android no permitió conservar el acceso a esta carpeta");}
    }
    private void updateEngine(){
        if(updating)return;
        DownloadQueueStore queue=new DownloadQueueStore(this);
        JSONArray jobs=queue.all();
        for(int i=0;i<jobs.length();i++){
            JSONObject j=jobs.optJSONObject(i);
            if(j!=null&&"running".equals(j.optString("status"))){
                toast("Espera a que termine la descarga actual");return;
            }
        }
        if(NetworkPolicy.isMetered(this)){
            new AlertDialog.Builder(this).setTitle("Actualizar usando datos móviles")
                .setMessage("La actualización puede consumir datos. ¿Continuar?")
                .setNegativeButton("Cancelar",null)
                .setPositiveButton("Continuar",(d,w)->runUpdate()).show();
        }else runUpdate();
    }
    private void runUpdate(){
        updating=true;
        engineButton.setEnabled(false);
        engineLabel.setText("Comprobando actualización estable de yt-dlp…");
        showEngineIssue("");
        worker.execute(()->{
            try{
                EngineHealth.UpdateResult result=EngineHealth.updateStableDetailed(getApplicationContext());
                runOnUiThread(()->{
                    engineLabel.setText(result.status);
                    showEngineIssue(result.verified ? "" :
                        getSharedPreferences("apex_descarga",MODE_PRIVATE)
                        .getString("engine_update_issue",""));
                });
            }catch(Exception ex){
                String friendly=EngineHealth.describeFailure(ex);
                runOnUiThread(()->{
                    engineLabel.setText(friendly);
                    showEngineIssue("No se ha confirmado una actualización. Tus descargas guardadas permanecen intactas.");
                });
            }finally{
                updating=false;
                runOnUiThread(()->engineButton.setEnabled(true));
            }
        });
    }
    private void showEngineIssue(String issue) {
        if(engineIssueLabel==null)return;
        engineIssueLabel.setVisibility(issue==null||issue.isEmpty()?View.GONE:View.VISIBLE);
        engineIssueLabel.setText(issue==null||issue.isEmpty()?"":"Última incidencia: "+issue);
    }
    private static String brief(Exception ex){String message=String.valueOf(ex.getMessage());return message.length()>110?message.substring(0,110)+"…":message;}
    private void toast(String s){android.widget.Toast.makeText(this,s,android.widget.Toast.LENGTH_SHORT).show();}
    @Override protected void onDestroy(){worker.shutdown();super.onDestroy();}
}
