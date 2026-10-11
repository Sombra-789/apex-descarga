package android.net;
public class NetworkCapabilities {
 public static final int NET_CAPABILITY_INTERNET=1,TRANSPORT_WIFI=2;
 boolean wifi;public NetworkCapabilities(boolean wifi){this.wifi=wifi;}
 public boolean hasCapability(int val){return true;}
 public boolean hasTransport(int val){return wifi;}
}
