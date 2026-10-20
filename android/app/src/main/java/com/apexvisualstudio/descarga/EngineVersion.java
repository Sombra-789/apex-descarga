package com.apexvisualstudio.descarga;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Parses engine version labels without Android dependencies.
 * Upstream may return a bare date or a string prefixed with "yt-dlp ".
 */
public final class EngineVersion {
    private EngineVersion() {}
    private static final Pattern VERSION = Pattern.compile(
        "(?<![0-9])(?:20[0-9]{2})\\.[0-9]{1,2}\\.[0-9]{1,2}(?:[-+._][A-Za-z0-9._+-]+)?"
    );
    public static String normalize(String value) {
        if (value == null) return "";
        Matcher match = VERSION.matcher(value.trim());
        return match.find() ? match.group() : "";
    }
    public static boolean isRecognized(String value) {
        return !normalize(value).isEmpty();
    }
}
