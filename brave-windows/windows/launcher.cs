// Apex Video Downloader Native Messaging launcher, Windows .NET Framework 4.x.
// Compiled locally using Windows PowerShell 5.1 Add-Type; no downloaded EXE.
// IMPORTANT: stdout must contain only protocol-framed UTF-8 JSON bytes.
using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Text;
using System.Threading;

internal static class ApexNativeLauncher
{
    private static void CopyStream(Stream source, Stream target)
    {
        try {
            byte[] buffer = new byte[32768];
            int count;
            while ((count = source.Read(buffer, 0, buffer.Length)) > 0) {
                target.Write(buffer, 0, count);
                target.Flush();
            }
        } catch (IOException) {
            // The browser may close the native-messaging pipe at any moment.
        } catch (ObjectDisposedException) {
        }
    }

    private static int Main(string[] args)
    {
        try {
            string directory = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            string python = File.ReadAllText(Path.Combine(directory, "python.path"), Encoding.UTF8).Trim();
            string script = Path.Combine(directory, "host.py");
            if (!File.Exists(python) || !File.Exists(script)) {
                Console.Error.WriteLine("Apex: falta Python o host.py. Ejecuta INSTALAR.cmd nuevamente.");
                return 2;
            }

            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = python;
            start.Arguments = "-u \"" + script.Replace("\"", "\\\"") + "\"";
            start.WorkingDirectory = directory;
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            start.RedirectStandardInput = true;
            start.RedirectStandardOutput = true;
            start.RedirectStandardError = true;

            using (Process child = Process.Start(start)) {
                if (child == null) return 3;
                Thread input = new Thread(() => {
                    try { CopyStream(Console.OpenStandardInput(), child.StandardInput.BaseStream); }
                    finally { try { child.StandardInput.Close(); } catch { } }
                });
                input.IsBackground = true;
                input.Start();

                Thread error = new Thread(() => CopyStream(child.StandardError.BaseStream, Console.OpenStandardError()));
                error.IsBackground = true;
                error.Start();

                // Preserve each protocol byte; no text encoding / newline conversion.
                CopyStream(child.StandardOutput.BaseStream, Console.OpenStandardOutput());
                child.WaitForExit();
                return child.ExitCode;
            }
        } catch (Exception ex) {
            Console.Error.WriteLine("Apex Native Messaging launcher: " + ex.Message);
            return 1;
        }
    }
}
