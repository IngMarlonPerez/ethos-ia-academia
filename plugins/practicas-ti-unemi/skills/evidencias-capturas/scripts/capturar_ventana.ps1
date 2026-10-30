<#
capturar_ventana.ps1 — captura UNA ventana por su título, con PrintWindow, aunque otra
ventana esté encima. NO usa CopyFromScreen del escritorio: ese método captura lo que
esté al frente (p. ej. la propia conversación con Claude) y puede filtrar datos privados.

Uso:
  pwsh -File capturar_ventana.ps1 -Titulo "sistema_experto.py - Visual Studio Code" -Png "C:\ruta\captura.png"

Antes de capturar:
- Abre el archivo/programa (p. ej. `code -n archivo.py`). Si VS Code muestra «Confianza en el
  área de trabajo / modo restringido», NO pulses «Confiar» (cambia la seguridad de VS Code):
  cierra esa pestaña con Ctrl+W y vuelve a abrir el archivo.
- Revisa la imagen resultante con Read antes de usarla: debe mostrar solo lo que se quiere
  evidenciar (sin rutas de otros proyectos, correos ni conversaciones).
#>
param(
  [Parameter(Mandatory)][string]$Titulo,
  [Parameter(Mandatory)][string]$Png
)
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text; using System.Collections.Generic;
public class CapW {
 public delegate bool EnumProc(IntPtr h, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
 [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint f);
 [StructLayout(LayoutKind.Sequential)] public struct RECT {public int L,T,R,B;}
 public static List<IntPtr> Find(string part){ var l=new List<IntPtr>(); EnumWindows((h,x)=>{ if(IsWindowVisible(h)){var s=new StringBuilder(256); GetWindowText(h,s,256); if(s.ToString().Contains(part)) l.Add(h);} return true;},IntPtr.Zero); return l; }
}
"@
$hs = [CapW]::Find($Titulo)
if ($hs.Count -eq 0) { throw "No hay una ventana visible con '$Titulo' en el título." }
$h = $hs[0]
$r = New-Object CapW+RECT; [CapW]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.R - $r.L; $hh = $r.B - $r.T
$bmp = New-Object Drawing.Bitmap $w, $hh
$g = [Drawing.Graphics]::FromImage($bmp); $hdc = $g.GetHdc()
$ok = [CapW]::PrintWindow($h, $hdc, 2); $g.ReleaseHdc($hdc)
New-Item -ItemType Directory -Force (Split-Path $Png) | Out-Null
$bmp.Save($Png)
"Captura ($w x $hh, PrintWindow=$ok): $Png"
