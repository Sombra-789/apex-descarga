package com.apexvisualstudio.descarga;

import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.Context;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Environment;
import android.provider.DocumentsContract;
import android.provider.MediaStore;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Locale;
import java.util.UUID;

/** Keeps downloads in app-private temporary storage until export into a user-visible collection. */
public final class DownloadStorage {
    private static final String PREFS = "apex_descarga";
    private static final String KEY_TREE = "download_tree";
    private final Context context;
    private final SharedPreferences prefs;

    public DownloadStorage(Context context) {
        this.context = context.getApplicationContext();
        this.prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    public File createJobDirectory() throws IOException {
        File root = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
        if (root == null) root = context.getFilesDir();
        File directory = new File(root, "job_" + UUID.randomUUID());
        if (!directory.mkdirs()) throw new IOException("No se pudo preparar el espacio de descarga.");
        return directory;
    }

    public boolean hasCustomFolder() {
        return !prefs.getString(KEY_TREE, "").isEmpty();
    }

    public String destinationLabel() {
        return hasCustomFolder() ? "Carpeta elegida · Android" : "Descargas / Apex Descarga";
    }

    public void saveTree(Uri uri) {
        prefs.edit().putString(KEY_TREE, uri.toString()).apply();
    }

    public void resetTree() {
        prefs.edit().remove(KEY_TREE).apply();
    }

    public Uri publish(File source) throws IOException {
        if (source == null || !source.isFile() || source.length() <= 0) {
            throw new IOException("No se encontró un archivo multimedia válido.");
        }
        String name = safeFilename(source.getName());
        String mime = mimeFor(name);
        String tree = prefs.getString(KEY_TREE, "");
        ContentResolver resolver = context.getContentResolver();
        Uri destination;
        if (!tree.isEmpty()) {
            Uri parent = Uri.parse(tree);
            try {
                Uri document = DocumentsContract.buildDocumentUriUsingTree(
                        parent, DocumentsContract.getTreeDocumentId(parent));
                destination = DocumentsContract.createDocument(resolver, document, mime, name);
            } catch (SecurityException e) {
                throw new IOException("Se perdió el permiso para la carpeta elegida. Selecciónala nuevamente.", e);
            }
            if (destination == null) throw new IOException("No se pudo crear el archivo en la carpeta elegida.");
            try {
                copy(resolver, source, destination);
            } catch (IOException e) {
                resolver.delete(destination, null, null);
                throw e;
            }
        } else {
            ContentValues values = new ContentValues();
            values.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
            values.put(MediaStore.MediaColumns.MIME_TYPE, mime);
            values.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/Apex Descarga/");
            values.put(MediaStore.MediaColumns.IS_PENDING, 1);
            Uri collection = MediaStore.Downloads.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY);
            destination = resolver.insert(collection, values);
            if (destination == null) throw new IOException("Android no permitió guardar en Descargas.");
            try {
                copy(resolver, source, destination);
                ContentValues ready = new ContentValues();
                ready.put(MediaStore.MediaColumns.IS_PENDING, 0);
                resolver.update(destination, ready, null, null);
            } catch (IOException e) {
                resolver.delete(destination, null, null);
                throw e;
            }
        }
        return destination;
    }

    private static void copy(ContentResolver resolver, File source, Uri uri) throws IOException {
        try (FileInputStream input = new FileInputStream(source);
             OutputStream output = resolver.openOutputStream(uri, "w")) {
            if (output == null) throw new IOException("No se pudo escribir el archivo elegido.");
            byte[] buffer = new byte[64 * 1024];
            int len;
            while ((len = input.read(buffer)) >= 0) {
                if (len > 0) output.write(buffer, 0, len);
            }
        }
    }

    public static String safeFilename(String original) {
        String name = original == null ? "descarga" : original;
        name = name.replaceAll("[\\\\/:*?\"<>|\\p{Cntrl}]", "_").trim();
        if (name.isEmpty() || name.equals(".") || name.equals("..")) name = "descarga";
        return name.length() > 180 ? name.substring(0, 180) : name;
    }

    private static String mimeFor(String name) {
        String lower = name.toLowerCase(Locale.ROOT);
        if (lower.endsWith(".mp3")) return "audio/mpeg";
        if (lower.endsWith(".m4a")) return "audio/mp4";
        if (lower.endsWith(".mp4")) return "video/mp4";
        if (lower.endsWith(".webm")) return "video/webm";
        if (lower.endsWith(".mkv")) return "video/x-matroska";
        return "application/octet-stream";
    }

    public static void cleanup(File dir) {
        if (dir == null || !dir.exists()) return;
        File[] items = dir.listFiles();
        if (items != null) {
            for (File child : items) {
                if (child.isDirectory()) cleanup(child);
                else child.delete();
            }
        }
        dir.delete();
    }
}
