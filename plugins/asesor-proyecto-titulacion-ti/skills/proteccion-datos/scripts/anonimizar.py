# -*- coding: utf-8 -*-
"""
anonimizar.py — seudonimiza las columnas personales de uno o varios CSV con
una semilla fija, conservando EXACTAMENTE las demás columnas (así ninguna
métrica del modelo cambia).

Decisiones (tomadas en la tesis VicMar Data AI, LOPDP):
  - Cédula ecuatoriana ficticia: 10 dígitos con dígito verificador válido
    (módulo 10) pero con código de provincia «00», que el Registro Civil no
    asigna: nunca coincide con una persona real.
  - El mismo valor original recibe el mismo seudónimo en TODOS los archivos,
    para que las tablas sigan unidas (p. ej. alumnos ↔ historial).
  - NO se guarda la tabla original → seudónimo: permitiría revertir la
    anonimización (sería, en sí misma, un dato personal).
  - Escribe en una carpeta de salida; los originales se MUEVEN fuera del
    repositorio a mano, con confirmación de la usuaria. Nunca se borran.

Tipos de columna: cedula_ec, id_numerico, nombres, apellidos, nombre_completo,
correo, telefono, texto.

Uso:
    python anonimizar.py --archivos alumnos.csv historial.csv --salida datos_anon/
        --columna cedula=cedula_ec --columna apellidos=apellidos --columna nombres=nombres
        [--genero genero] [--semilla 20260909]
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

NOMBRES_F = ['Ana', 'María', 'Lucía', 'Valeria', 'Camila', 'Daniela', 'Gabriela', 'Andrea', 'Paula', 'Sofía', 'Isabel',
             'Carolina', 'Fernanda', 'Natalia', 'Mónica', 'Patricia', 'Rosa', 'Elena', 'Julia', 'Carla', 'Diana', 'Laura']
NOMBRES_M = ['Juan', 'Carlos', 'Luis', 'José', 'Andrés', 'Diego', 'Mateo', 'Santiago', 'Pablo', 'Javier', 'Miguel',
             'Daniel', 'Fernando', 'Ricardo', 'Sebastián', 'Tomás', 'Nicolás', 'Gustavo', 'Hugo', 'Iván', 'Rafael', 'Samuel']
APELLIDOS = ['Aguirre', 'Alvarado', 'Andrade', 'Bravo', 'Cabrera', 'Castillo', 'Cedeño', 'Cevallos', 'Chávez', 'Delgado',
             'Espinoza', 'Flores', 'Guerrero', 'Herrera', 'Jiménez', 'León', 'Macías', 'Mendoza', 'Mora', 'Moreira',
             'Navarrete', 'Ortiz', 'Paredes', 'Quintero', 'Ramírez', 'Reyes', 'Rivera', 'Salazar', 'Sánchez', 'Suárez',
             'Torres', 'Valencia', 'Vargas', 'Vera', 'Villacís', 'Zambrano']
TIPOS = ['cedula_ec', 'id_numerico', 'nombres', 'apellidos', 'nombre_completo', 'correo', 'telefono', 'texto']


def digito_verificador(nueve: str) -> int:
    """Módulo 10 de la cédula ecuatoriana sobre los 9 primeros dígitos."""
    total = 0
    for i, d in enumerate(nueve):
        v = int(d) * (2 if i % 2 == 0 else 1)
        total += v - 9 if v > 9 else v
    return (10 - total % 10) % 10


def cedula_valida(ced: str) -> bool:
    return len(ced) == 10 and ced.isdigit() and 1 <= int(ced[:2]) <= 24 and int(ced[2]) < 6 and \
        digito_verificador(ced[:9]) == int(ced[9])


class Seudonimizador:
    def __init__(self, semilla: int):
        self.rng = random.Random(semilla)
        self.mapas: dict[str, dict[str, str]] = {t: {} for t in TIPOS}
        self.usados: set[str] = set()

    def _unico(self, generar) -> str:
        while True:
            v = generar()
            if v not in self.usados:
                self.usados.add(v)
                return v

    def valor(self, tipo: str, original: str, genero: str = '') -> str:
        if original in ('', None):
            return original
        mapa = self.mapas[tipo]
        if original in mapa:
            return mapa[original]
        r = self.rng
        nombres = NOMBRES_F if str(genero).upper().startswith('F') else NOMBRES_M
        if tipo == 'cedula_ec':
            def gen():
                nueve = '00' + str(r.randint(0, 5)) + f'{r.randint(0, 999999):06d}'
                return nueve + str(digito_verificador(nueve))
            nuevo = self._unico(gen)
        elif tipo == 'id_numerico':
            nuevo = self._unico(lambda: str(r.randint(10 ** (len(original) - 1), 10 ** len(original) - 1)) if original.isdigit()
                                else f'ID{r.randint(0, 10 ** 9):09d}')
        elif tipo == 'nombres':
            nuevo = f'{r.choice(nombres)} {r.choice(nombres)}'
        elif tipo == 'apellidos':
            nuevo = f'{r.choice(APELLIDOS)} {r.choice(APELLIDOS)}'
        elif tipo == 'nombre_completo':
            nuevo = f'{r.choice(APELLIDOS)} {r.choice(APELLIDOS)} {r.choice(nombres)}'
        elif tipo == 'correo':
            nuevo = self._unico(lambda: f'persona{r.randint(0, 10 ** 7):07d}@ejemplo.edu.ec')
        elif tipo == 'telefono':
            nuevo = self._unico(lambda: f'0900{r.randint(0, 999999):06d}')
        else:
            nuevo = f'Persona {len(mapa) + 1}'
        mapa[original] = nuevo
        return nuevo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--archivos', nargs='+', required=True)
    ap.add_argument('--salida', required=True, help='carpeta de salida (no se sobrescriben los originales)')
    ap.add_argument('--columna', action='append', required=True, help='nombre=tipo; tipos: ' + ', '.join(TIPOS))
    ap.add_argument('--genero', help='columna de género (F/M) para nombres coherentes')
    ap.add_argument('--semilla', type=int, default=20260909)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    columnas = {}
    for c in a.columna:
        nombre, _, tipo = c.partition('=')
        if tipo not in TIPOS:
            sys.exit(f'Tipo desconocido: {tipo}. Usa {TIPOS}')
        columnas[nombre] = tipo
    salida = Path(a.salida)
    salida.mkdir(parents=True, exist_ok=True)
    s = Seudonimizador(a.semilla)
    for archivo in a.archivos:
        origen = Path(archivo)
        destino = salida / origen.name
        if destino.resolve() == origen.resolve():
            sys.exit('La salida no puede ser el mismo archivo de origen.')
        with open(origen, encoding='utf-8-sig', newline='') as f:
            lector = csv.DictReader(f)
            campos = list(lector.fieldnames or [])
            filas = list(lector)
        presentes = [c for c in columnas if c in campos]
        for fila in filas:
            for c in presentes:
                fila[c] = s.valor(columnas[c], fila[c], fila.get(a.genero, '') if a.genero else '')
        with open(destino, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            w.writerows(filas)
        print(f'{origen.name}: {len(filas)} filas; columnas seudonimizadas: {", ".join(presentes) or "ninguna"} → {destino}')
    print('Listo. No se guardó ninguna tabla de correspondencia. Mueve los originales fuera del repositorio (no los borres).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
