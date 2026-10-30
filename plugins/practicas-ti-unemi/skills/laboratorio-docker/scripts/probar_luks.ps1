<#
probar_luks.ps1 — cifrado de DISCO COMPLETO con LUKS2 (dm-crypt, el equivalente abierto de
BitLocker) dentro de una máquina virtual Linux (Docker Desktop sobre WSL2).

Es un entorno virtualizado y desechable: crea una imagen de disco de 100 MB dentro del
contenedor, la cifra, la formatea, escribe un archivo, la cierra, comprueba que una clave
incorrecta se rechaza y que la correcta recupera el archivo con el mismo hash. No toca
los discos de Windows ni la seguridad del equipo. La contraseña es aleatoria, vive solo
dentro del contenedor y nunca se imprime.

Uso:
  pwsh -File probar_luks.ps1 -Salida "C:\ruta\laboratorio" [-MB 100]
Salida: luks_log.txt con la salida real y los tiempos.
Requiere: Docker Desktop (el contenedor usa --privileged para dispositivos loop/dm-crypt).
#>
param(
  [Parameter(Mandatory)][string]$Salida,
  [int]$MB = 100
)
New-Item -ItemType Directory -Force $Salida | Out-Null
$img = "practicas-ti/lab:1.0"
if (-not (docker images -q $img)) { docker build -t $img "$PSScriptRoot\..\docker" | Out-Null }

$sh = @'
set -e
t() { date +%s.%N; }
dif() { awk -v a="$1" -v b="$2" 'BEGIN{printf "%.2f", b-a}'; }
echo "$ uname -sr"; uname -sr
dd if=/dev/zero of=/tmp/disco.img bs=1M count=__MB__ status=none
LOOP=$(losetup -f --show /tmp/disco.img)
echo "$ losetup -f --show disco.img   ->  $LOOP (imagen de __MB__ MB)"
PW=$(head -c 12 /dev/urandom | base64)
s=$(t); echo -n "$PW" | cryptsetup luksFormat --batch-mode --type luks2 "$LOOP" -; e=$(t)
echo "$ cryptsetup luksFormat --type luks2 $LOOP     [$(dif $s $e) s]"
s=$(t); echo -n "$PW" | cryptsetup open "$LOOP" discoseguro -; e=$(t)
echo "$ cryptsetup open $LOOP discoseguro            [$(dif $s $e) s]"
mkfs.ext4 -q /dev/mapper/discoseguro
mkdir -p /mnt/seguro; mount /dev/mapper/discoseguro /mnt/seguro
head -c 5000000 /dev/urandom > /mnt/seguro/archivo.bin
H1=$(sha256sum /mnt/seguro/archivo.bin | cut -c1-16)
echo "$ archivo.bin (5 MB) escrito en el disco cifrado  sha256: $H1..."
umount /mnt/seguro; cryptsetup close discoseguro
echo "$ umount + cryptsetup close  (el disco queda cifrado e ilegible)"
echo "$ strings disco.img | grep -c 'archivo.bin'  ->  $(strings /tmp/disco.img | grep -c 'archivo.bin' || true) coincidencias del nombre de archivo en el disco cifrado"
echo "$ cryptsetup open con clave INCORRECTA:"
if echo -n "clave-incorrecta" | cryptsetup open "$LOOP" discoseguro - 2>&1; then echo "  (ERROR: abrio con clave incorrecta)"; else echo "  -> rechazada"; fi
echo -n "$PW" | cryptsetup open "$LOOP" discoseguro -
mount /dev/mapper/discoseguro /mnt/seguro
H2=$(sha256sum /mnt/seguro/archivo.bin | cut -c1-16)
echo "$ cryptsetup open con la clave correcta -> sha256: $H2...  igual al original: $([ "$H1" = "$H2" ] && echo SI || echo NO)"
umount /mnt/seguro; cryptsetup close discoseguro
echo "$ cryptsetup luksDump (resumen)"
cryptsetup luksDump "$LOOP" | grep -E "^Version|cipher:|cipher key|PBKDF:|Hash:" | head -6
losetup -d "$LOOP"
'@
$sh = $sh.Replace("__MB__", "$MB")
$log = Join-Path $Salida "luks_log.txt"
docker run --rm --privileged $img sh -c ($sh -replace "`r", "") 2>&1 | Tee-Object $log
"Registro: $log"
