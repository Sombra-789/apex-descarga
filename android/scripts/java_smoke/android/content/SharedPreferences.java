package android.content;
public interface SharedPreferences {
 boolean getBoolean(String name,boolean fallback);int getInt(String name,int fallback);
 String getString(String name,String fallback);
 Editor edit();
 interface Editor {Editor putBoolean(String name,boolean value);Editor putInt(String name,int value);Editor putLong(String name,long value);Editor putString(String name,String value);void apply();}
}
