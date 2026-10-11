package com.apexvisualstudio.descarga;

import android.content.Context;
import android.content.SharedPreferences;

/** Detect appearance changes without modifying existing 0.5 preference keys. */
public final class ThemeIdentity {
    private ThemeIdentity(){}
    public static String token(Context ctx){
        SharedPreferences p=ctx.getSharedPreferences("apex_descarga",Context.MODE_PRIVATE);
        return p.getInt("theme",0)+":"+p.getBoolean("show_logo",true)+":"
            +p.getInt("custom_primary",0)+":"+p.getInt("custom_secondary",0)+":"
            +p.getInt("custom_accent",0);
    }
}
