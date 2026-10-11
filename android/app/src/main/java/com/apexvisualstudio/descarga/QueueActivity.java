package com.apexvisualstudio.descarga;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import org.json.JSONArray;
import org.json.JSONObject;

/** Dedicated, uncluttered queue with artwork, status and actions for each job. */
public final class QueueActivity extends Activity {
    private DownloadQueueStore store;
    private ApexUi ui;
    private LinearLayout list;
    private TextView summary;
    private String filter="all";
    private BroadcastReceiver receiver;
    private String oldPalette="";
    private final java.util.LinkedHashMap<String,Button> filterButtons=new java.util.LinkedHashMap<>();
    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        ui=new ApexUi(this);store=new DownloadQueueStore(this);oldPalette=ThemeIdentity.token(this);
        getWindow().setStatusBarColor(ApexUi.BG);getWindow().setNavigationBarColor(ApexUi.BG);
        LinearLayout root=ui.scaffold(this,"cola");
        TextView head=ui.heading("Descargas");root.addView(head);
        summary=ui.text("Actualizando cola…",12,ApexUi.MUTED,false);LinearLayout.LayoutParams sh=ui.lp(-1,-2);sh.topMargin=ui.dp(7);root.addView(summary,sh);
        LinearLayout filters=ui.row();LinearLayout.LayoutParams fl=ui.lp(-1,-2);fl.topMargin=ui.dp(18);root.addView(filters,fl);
        for(String[] item:new String[][]{{"Todas","all"},{"Activas","active"},{"Listas","done"},{"Fallos","failed"}}){
            Button b=ui.button(item[0],false);b.setTextSize(11);
            filterButtons.put(item[1],b);
            b.setOnClickListener(v->{filter=item[1];render();});
            filters.addView(b,new LinearLayout.LayoutParams(0,ui.dp(43),1));
        }
        list=ui.vert();LinearLayout.LayoutParams ll=ui.lp(-1,-2);ll.topMargin=ui.dp(12);root.addView(list,ll);
        Button resume=ui.button("↻  Reanudar interrumpidas",false);
        resume.setOnClickListener(v->{store.resumePending();if(store.pendingCount()>0)DownloadService.enqueue(this);render();});
        LinearLayout.LayoutParams rl=ui.lp(-1,ui.dp(48));rl.topMargin=ui.dp(16);root.addView(resume,rl);
        Button clear=ui.button("Limpiar trabajos finalizados",false);clear.setOnClickListener(v->new AlertDialog.Builder(this)
            .setTitle("Limpiar la cola")
            .setMessage("Se quitarán las entradas finalizadas, sin borrar los archivos de tu biblioteca.")
            .setNegativeButton("Cancelar",null).setPositiveButton("Limpiar",(d,w)->{store.clearFinished();render();}).show());
        root.addView(clear,ui.lp(-1,ui.dp(48)));
        render();
    }
    @Override protected void onResume(){
        super.onResume();
        if(!oldPalette.equals(ThemeIdentity.token(this))){recreate();return;}
        render();
    }
    @Override protected void onStart(){super.onStart();receiver=new BroadcastReceiver(){@Override public void onReceive(Context c,Intent i){render();}};
        IntentFilter f=new IntentFilter(DownloadService.CHANGED);
        if(Build.VERSION.SDK_INT>=33)registerReceiver(receiver,f,Context.RECEIVER_NOT_EXPORTED);else registerReceiver(receiver,f);
        render();
    }
    @Override protected void onStop(){if(receiver!=null){unregisterReceiver(receiver);receiver=null;}super.onStop();}
    private boolean matches(String status){
        switch(filter){case "active":return status.equals("running")||status.equals("waiting")||status.equals("paused");
        case "done":return status.equals("done");case "failed":return status.equals("failed")||status.equals("cancelled");default:return true;}
    }
    private void render(){
        if(list==null)return;
        list.removeAllViews();
        for(java.util.Map.Entry<String,Button> tab:filterButtons.entrySet()){
            tab.getValue().setBackground(ui.surface(13,filter.equals(tab.getKey())?ui.accent:0xFF304166));
        }
        JSONArray jobs=store.all();int running=0,wait=0,done=0,shown=0;
        for(int i=0;i<jobs.length();i++){JSONObject j=jobs.optJSONObject(i);if(j==null)continue;
            String st=j.optString("status");if(st.equals("running"))running++;if(st.equals("waiting"))wait++;if(st.equals("done"))done++;}
        summary.setText(running+" descargando  ·  "+wait+" pendientes  ·  "+done+" completadas");
        for(int i=jobs.length()-1;i>=0;i--){
            JSONObject job=jobs.optJSONObject(i);if(job==null||!matches(job.optString("status")))continue;
            shown++;String status=job.optString("status");String id=job.optString("id");
            LinearLayout card=ui.queueCard(job,null);
            LinearLayout actions=ui.row();LinearLayout.LayoutParams al=ui.lp(-1,-2);al.topMargin=ui.dp(8);
            if(status.equals("running")||status.equals("waiting")){
                Button cancel=ui.button("Cancelar",false);cancel.setOnClickListener(v->{DownloadService.cancel(this,id);});
                actions.addView(cancel,new LinearLayout.LayoutParams(0,ui.dp(42),1));
            }else if(status.equals("failed")||status.equals("cancelled")||status.equals("paused")){
                Button retry=ui.button("Reintentar",false);retry.setOnClickListener(v->{store.retry(id);DownloadService.enqueue(this);render();});
                actions.addView(retry,new LinearLayout.LayoutParams(0,ui.dp(42),1));
            }else if(status.equals("done")){
                String uri=job.optString("uri");
                if(!uri.isEmpty()){
                    Button open=ui.button("Abrir archivo",false);
                    open.setOnClickListener(v->{try{
                        Intent action=new Intent(Intent.ACTION_VIEW);action.setDataAndType(Uri.parse(uri),
                            "mp3".equals(job.optString("format"))?"audio/mpeg":"video/mp4");
                        action.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);startActivity(action);
                    }catch(Exception ex){android.widget.Toast.makeText(this,"No se pudo abrir el archivo",android.widget.Toast.LENGTH_SHORT).show();}});
                    actions.addView(open,new LinearLayout.LayoutParams(0,ui.dp(42),1));
                }
            }
            if(actions.getChildCount()>0)card.addView(actions,al);
            LinearLayout.LayoutParams params=ui.lp(-1,-2);params.bottomMargin=ui.dp(11);list.addView(card,params);
        }
        if(shown==0){TextView empty=ui.text("No hay descargas en esta sección.",14,ApexUi.MUTED,false);empty.setPadding(ui.dp(10),ui.dp(32),0,ui.dp(32));list.addView(empty);}
    }
}
