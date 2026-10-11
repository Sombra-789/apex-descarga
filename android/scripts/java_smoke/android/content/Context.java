package android.content;
import android.net.*;import java.io.File;import java.util.*;
public class Context {
 public static final int MODE_PRIVATE=0;public static final String CONNECTIVITY_SERVICE="connectivity";
 private final HashMap<String,Object> map=new HashMap<>();public ConnectivityManager network=new ConnectivityManager();
 public Context getApplicationContext(){return this;}
 public Object getSystemService(String name){return network;}
 public File getExternalFilesDir(String folder){return new File("/tmp");}
 public File getFilesDir(){return new File("/tmp");}
 public SharedPreferences getSharedPreferences(String name,int mode){return new SharedPreferences(){
 public boolean getBoolean(String n,boolean f){return (Boolean)map.getOrDefault(n,f);}
 public int getInt(String n,int f){return (Integer)map.getOrDefault(n,f);}
 public String getString(String n,String f){return (String)map.getOrDefault(n,f);}
 public SharedPreferences.Editor edit(){return new SharedPreferences.Editor(){
 public SharedPreferences.Editor putBoolean(String n,boolean v){map.put(n,v);return this;}
 public SharedPreferences.Editor putInt(String n,int v){map.put(n,v);return this;}
 public SharedPreferences.Editor putLong(String n,long v){map.put(n,v);return this;}
 public SharedPreferences.Editor putString(String n,String v){map.put(n,v);return this;}
 public void apply(){}
 };}
 };}
}
