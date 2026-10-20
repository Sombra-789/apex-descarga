package com.apexvisualstudio.descarga;

import android.content.Context;
import android.content.SharedPreferences;
import com.yausername.youtubedl_android.YoutubeDL;
import java.util.Locale;

/**
 * Conserves the upstream stable updater; does not download arbitrary binaries.
 * A successful updater call is not proof of a newly installed version unless the
 * installed version can be read and recognized afterwards.
 */
public final class EngineHealth {
    private EngineHealth(){}

    public static final class UpdateResult {
        public final String version;
        public final boolean verified;
        public final boolean changed;
        public final String status;

        private UpdateResult(String version, boolean verified, boolean changed, String status) {
            this.version = version;
            this.verified = verified;
            this.changed = changed;
            this.status = status;
        }
    }

    public static boolean versionLooksValid(String version) {
        return EngineVersion.isRecognized(version);
    }

    public static String describeFailure(Exception ex) {
        String kind = ex.getClass().getSimpleName();
        String detail = ex.getMessage();
        if (detail == null || detail.trim().isEmpty()) detail = "sin detalle adicional";
        detail = detail.replace('\n', ' ').replace('\r', ' ').trim();
        if (detail.length() > 110) detail = detail.substring(0, 110) + "…";
        String lower = (kind + " " + detail).toLowerCase(Locale.ROOT);
        if (lower.contains("timeout") || lower.contains("unknownhost") ||
                lower.contains("connection") || lower.contains("network"))
            return "Error de conexión al actualizar (" + kind + "). Revisa Internet e inténtalo más tarde.";
        if (lower.contains("ssl") || lower.contains("certificate"))
            return "No se pudo verificar la conexión segura del actualizador (" + kind + ").";
        return "El actualizador no completó la operación (" + kind + "): " + detail;
    }

    private static String safeVersion(YoutubeDL engine, Context context) {
        try {
            return EngineVersion.normalize(engine.versionName(context));
        } catch (Exception ignored) {
            return "";
        }
    }

    public static UpdateResult updateStableDetailed(Context context) throws Exception {
        SharedPreferences prefs = context.getSharedPreferences("apex_descarga", Context.MODE_PRIVATE);
        synchronized (DownloadService.ENGINE_LOCK) {
            YoutubeDL engine = YoutubeDL.getInstance();
            String before = "";
            try {
                engine.init(context.getApplicationContext());
                before = safeVersion(engine, context);
                prefs.edit()
                    .putString("engine_previous_version", before)
                    .putLong("engine_last_checked", System.currentTimeMillis())
                    .apply();

                engine.updateYoutubeDL(context, YoutubeDL.UpdateChannel._STABLE);
                String after = safeVersion(engine, context);

                if (after.isEmpty()) {
                    // The updater returned, but a readable installed version is absent.
                    // Report uncertainty instead of throwing a false IllegalStateException.
                    String warning = "No fue posible confirmar la versión de yt-dlp después de actualizar.";
                    prefs.edit()
                        .putString("engine_update_issue", warning)
                        .putString("engine_version_last", before)
                        .putLong("engine_updated_at", System.currentTimeMillis())
                        .apply();
                    return new UpdateResult(before, false, false,
                        warning + " Comprueba las descargas antes de volver a intentar.");
                }

                boolean changed = !before.isEmpty() && !before.equals(after);
                prefs.edit()
                    .putString("engine_version_last", after)
                    .putString("engine_update_issue", "")
                    .putLong("engine_updated_at", System.currentTimeMillis())
                    .apply();
                String status = changed
                    ? "yt-dlp actualizado y verificado: " + after
                    : "yt-dlp verificado: " + after + ". El motor no informó una versión diferente.";
                return new UpdateResult(after, true, changed, status);
            } catch (Exception ex) {
                // Do not erase the previous usable version or mark it updated.
                String issue = describeFailure(ex);
                prefs.edit().putString("engine_update_issue", issue)
                    .putString("engine_version_last", before).apply();
                throw ex;
            }
        }
    }

    /** Original caller used by the scheduled updater. */
    public static String updateStable(Context context) throws Exception {
        return updateStableDetailed(context).version;
    }
}
