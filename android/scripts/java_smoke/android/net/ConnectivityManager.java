package android.net;
public class ConnectivityManager {
 public boolean wifi=false,metered=true;
 public Network getActiveNetwork(){return new Network();}
 public NetworkCapabilities getNetworkCapabilities(Network net){return new NetworkCapabilities(wifi);}
 public boolean isActiveNetworkMetered(){return metered;}
}
