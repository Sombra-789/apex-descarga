package com.apexvisualstudio.descarga;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.widget.ScrollView;
import android.graphics.drawable.ColorDrawable;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import org.json.JSONObject;
import java.util.Locale;

/** Small toolkit shared by queue, preview and library; no external UI dependencies. */
public final class ApexUi {
    public static final int BG=0xFF080D18, SURFACE=0xFF111A2B, WHITE=0xFFF3F7FF, MUTED=0xFF94A8C3;
    private final Context context;
    public final int primary,secondary,accent;
    public ApexUi(Context context){
        this.context=context;
        SharedPreferences p=context.getSharedPreferences("apex_descarga",Context.MODE_PRIVATE);
        int[][] colors={{0xFF277AFF,0xFF9B4AFF,0xFF38DAFF},{0xFF006BB9,0xFF12B8D8,0xFF5CE4FF},{0xFF7743E4,0xFFE06FFB,0xFFC58CFF},{0xFF0E9B7D,0xFF7CC940,0xFF57E5B1},{0xFFDB436F,0xFFFF974F,0xFFFFB6C3}};
        int theme=p.getInt("theme",0);
        primary=theme==5?p.getInt("custom_primary",colors[0][0]):colors[Math.min(4,Math.max(0,theme))][0];
        secondary=theme==5?p.getInt("custom_secondary",colors[0][1]):colors[Math.min(4,Math.max(0,theme))][1];
        accent=theme==5?p.getInt("custom_accent",colors[0][2]):colors[Math.min(4,Math.max(0,theme))][2];
    }
    public int dp(int v){return Math.round(v*context.getResources().getDisplayMetrics().density);}
    public LinearLayout vert(){LinearLayout l=new LinearLayout(context);l.setOrientation(LinearLayout.VERTICAL);return l;}
    public LinearLayout row(){LinearLayout l=new LinearLayout(context);l.setOrientation(LinearLayout.HORIZONTAL);l.setGravity(Gravity.CENTER_VERTICAL);return l;}
    public LinearLayout.LayoutParams lp(int w,int h){return new LinearLayout.LayoutParams(w,h);}
    public GradientDrawable surface(int radius,int border){
        GradientDrawable g=new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,new int[]{0xFF172238,0xFF111A2B});
        g.setCornerRadius(dp(radius));if(border!=0)g.setStroke(dp(1),border);return g;
    }
    public GradientDrawable pill(int color){GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(dp(100));return g;}
    public TextView text(String text,int size,int color,boolean bold){
        TextView v=new TextView(context);v.setText(text);v.setTextSize(size);v.setTextColor(color);
        if(bold)v.setTypeface(Typeface.DEFAULT,Typeface.BOLD);return v;
    }
    public TextView chip(String label,int tint){
        TextView t=text(label,10,tint,true);t.setGravity(Gravity.CENTER);t.setPadding(dp(10),dp(6),dp(10),dp(6));
        GradientDrawable shape=pill(0xFF1B2A43);t.setBackground(shape);return t;
    }
    public Button button(String label, boolean active){
        Button b=new Button(context);b.setText(label);b.setAllCaps(false);b.setTextSize(12);b.setTypeface(Typeface.DEFAULT,Typeface.BOLD);b.setTextColor(WHITE);
        if(active){GradientDrawable g=new GradientDrawable(GradientDrawable.Orientation.LEFT_RIGHT,new int[]{primary,secondary});g.setCornerRadius(dp(14));b.setBackground(g);}
        else b.setBackground(surface(14,0xFF26354E));
        return b;
    }
    public LinearLayout card(){LinearLayout c=vert();c.setPadding(dp(16),dp(16),dp(16),dp(16));c.setBackground(surface(19,0xFF263750));return c;}
    /** Persistent bottom navigation; actual Android views, not a screenshot. */
    public LinearLayout scaffold(Activity activity,String selected){
        activity.getWindow().setStatusBarColor(BG);
        activity.getWindow().setNavigationBarColor(BG);
        LinearLayout shell=vert();shell.setBackgroundColor(BG);
        ScrollView scroll=new ScrollView(activity);scroll.setBackgroundColor(BG);
        scroll.setFillViewport(false);scroll.setVerticalScrollBarEnabled(false);
        LinearLayout root=vert();root.setPadding(dp(20),dp(24),dp(20),dp(25));scroll.addView(root);
        shell.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        LinearLayout nav=row();nav.setPadding(dp(10),dp(7),dp(10),dp(7));nav.setBackgroundColor(0xFF0C1424);
        String[][] items={{"⌂","Inicio","inicio"},{"☷","Cola","cola"},{"▣","Biblioteca","biblioteca"},{"⚙","Ajustes","ajustes"}};
        for(String[] item:items){
            boolean active=item[2].equals(selected);
            LinearLayout cell=vert();cell.setGravity(Gravity.CENTER);
            TextView icon=text(item[0],23,active?accent:MUTED,true);icon.setGravity(Gravity.CENTER);
            TextView label=text(item[1],10,active?accent:MUTED,active);label.setGravity(Gravity.CENTER);
            cell.addView(icon);cell.addView(label);
            nav.addView(cell,new LinearLayout.LayoutParams(0,dp(60),1));
            cell.setContentDescription("Abrir "+item[1]);
            cell.setOnClickListener(v->{
                if(active)return;
                Class<?> target="inicio".equals(item[2])?MainActivity.class:
                    "cola".equals(item[2])?QueueActivity.class:
                    "biblioteca".equals(item[2])?LibraryActivity.class:SettingsActivity.class;
                Intent intent=new Intent(activity,target);
                intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP|Intent.FLAG_ACTIVITY_SINGLE_TOP);
                activity.startActivity(intent);
            });
        }
        shell.addView(nav,new LinearLayout.LayoutParams(-1,dp(74)));
        activity.setContentView(shell);
        return root;
    }
    public void addGap(LinearLayout parent,int size){View v=new View(context);parent.addView(v,new LinearLayout.LayoutParams(1,dp(size)));}
    public TextView heading(String text){return text(text,23,WHITE,true);}
    public LinearLayout box(LinearLayout root){LinearLayout c=card();LinearLayout.LayoutParams p=lp(-1,-2);p.topMargin=dp(15);root.addView(c,p);return c;}
    public void addAccentLabel(LinearLayout root,String label){TextView t=text(label,11,accent,true);t.setLetterSpacing(.07f);root.addView(t);}
    public TextView caption(String label){return text(label,12,MUTED,false);}

    public static String quality(int selection){switch(selection){case 1:return "480p";case 2:return "720p";case 3:return "1080p";case 4:return "4K";default:return "Mejor disponible";}}
    public static String status(String state){
        switch(state){case "running":return "DESCARGANDO";case "waiting":return "EN COLA";case "done":return "COMPLETADA";
        case "failed":return "ERROR";case "paused":return "INTERRUMPIDA";case "cancelled":return "CANCELADA";default:return "PENDIENTE";}
    }
    public static int statusColor(String state,int accent){
        switch(state){case "done":return 0xFF60E1AC;case "failed":return 0xFFFF8B9D;case "cancelled":return 0xFFA9B1C8;
        case "running":return accent;default:return 0xFFD2BBFF;}
    }
    public LinearLayout queueCard(JSONObject job,View.OnClickListener click){
        String state=job.optString("status","waiting"), title=job.optString("title",job.optString("name","Contenido"));
        LinearLayout block=card();
        LinearLayout main=row();
        ImageView art=new ImageView(context);art.setBackground(surface(12,0));art.setClipToOutline(true);
        String image=job.optString("thumbnail","");
        if(image.isEmpty())image=MediaMetadata.urlThumbnail(job.optString("url",""));
        ArtworkCache.attach(context,art,image);
        main.addView(art,new LinearLayout.LayoutParams(dp(88),dp(80)));
        LinearLayout info=vert();info.setPadding(dp(12),0,0,0);
        TextView titleText=text(title,14,WHITE,true);titleText.setMaxLines(2);titleText.setEllipsize(android.text.TextUtils.TruncateAt.END);
        info.addView(titleText);
        String author=job.optString("author","");String dur=job.optString("duration","");
        String sub=(!author.isEmpty()?author+" · ":"")+(!dur.isEmpty()?dur:job.optString("platform", ""));
        TextView authorText=text(sub,11,MUTED,false);authorText.setMaxLines(1);authorText.setEllipsize(android.text.TextUtils.TruncateAt.END);info.addView(authorText);
        LinearLayout labels=row();labels.setPadding(0,dp(7),0,0);
        labels.addView(chip(status(state),statusColor(state,accent)));
        TextView ext=text("  "+job.optString("format","mp4").toUpperCase(Locale.ROOT)+"  ·  "+quality(job.optInt("quality",0)),10,MUTED,false);
        labels.addView(ext);info.addView(labels);
        main.addView(info,new LinearLayout.LayoutParams(0,-2,1));block.addView(main);
        if("running".equals(state)||"done".equals(state)){
            ProgressBar bar=new ProgressBar(context,null,android.R.attr.progressBarStyleHorizontal);
            bar.setMax(100);bar.setProgress(job.optInt("progress",0));bar.setProgressTintList(android.content.res.ColorStateList.valueOf(accent));
            bar.setProgressBackgroundTintList(android.content.res.ColorStateList.valueOf(0xFF273750));
            LinearLayout.LayoutParams pp=lp(-1,dp(5));pp.topMargin=dp(14);block.addView(bar,pp);
        }
        String note=job.optString("note","");if(!note.isEmpty()){
            TextView noteText=text(note,11,"failed".equals(state)?0xFFFFB4BF:MUTED,false);
            noteText.setMaxLines(2);noteText.setEllipsize(android.text.TextUtils.TruncateAt.END);
            LinearLayout.LayoutParams np=lp(-1,-2);np.topMargin=dp(8);block.addView(noteText,np);
        }
        if(click!=null)block.setOnClickListener(click);
        return block;
    }
}
