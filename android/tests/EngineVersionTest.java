package com.apexvisualstudio.descarga;

/** Offline smoke tests: run via javac/java on GitHub Actions. */
public final class EngineVersionTest {
    private static void eq(String expected, String actual) {
        if (!expected.equals(actual))
            throw new AssertionError("Expected " + expected + " but got " + actual);
    }
    private static void truth(boolean expected, boolean actual) {
        if (expected != actual) throw new AssertionError("Unexpected validation result");
    }
    public static void main(String[] args) {
        eq("2026.08.19", EngineVersion.normalize("2026.08.19"));
        eq("2026.08.19", EngineVersion.normalize("yt-dlp 2026.08.19"));
        eq("2026.10.20", EngineVersion.normalize("Version: 2026.10.20"));
        eq("2026.10.20.1", EngineVersion.normalize("yt-dlp 2026.10.20.1"));
        eq("", EngineVersion.normalize(null));
        eq("", EngineVersion.normalize("unknown"));
        truth(true, EngineVersion.isRecognized("yt-dlp 2026.08.19"));
        truth(false, EngineVersion.isRecognized("unavailable"));
        System.out.println("PASS EngineVersion parsing");
    }
}
