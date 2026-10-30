# -*- coding: utf-8 -*-
"""PLANTILLA de pruebas para privacidad.py (cópiala a tests/ y ajusta el import
y la función que envía datos al proveedor externo)."""
from unittest import mock

from privacidad import enmascarar_cedula, enmascarar_filas, es_columna_personal

CEDULA = '0923456781'


def test_columnas_personales_se_reconocen():
    for c in ('cedula', 'Cédula', 'correo_electronico', 'telefono', 'nombres', 'apellidos'):
        assert es_columna_personal(c)
    assert not es_columna_personal('carrera')


def test_enmascarar_filas_no_deja_identificadores():
    cols, filas = enmascarar_filas(['cedula', 'nombres', 'carrera'],
                                   [[CEDULA, 'Ana Pérez', 'Software'], [CEDULA, 'Ana Pérez', 'Software'], ['0102030405', 'Luis', 'Redes']])
    texto = str(filas)
    assert CEDULA not in texto and 'Ana' not in texto
    assert filas[0][0] == filas[1][0]            # misma persona → mismo seudónimo
    assert filas[0][0] != filas[2][0]
    assert [f[2] for f in filas] == ['Software', 'Software', 'Redes']   # lo demás no cambia


def test_cedula_en_texto_libre_se_oculta():
    _, filas = enmascarar_filas(['detalle'], [[f'El estudiante {CEDULA} se retiró']])
    assert CEDULA not in filas[0][0]


def test_pantalla_muestra_solo_ultimos_digitos():
    assert enmascarar_cedula(CEDULA) == '******6781'


def test_lo_que_sale_al_proveedor_no_tiene_cedulas():
    """Intercepta el envío HTTP al proveedor externo y revisa el cuerpo.
    Ajusta 'mi_modulo.redactar' a la función real que llama al proveedor."""
    import mi_modulo  # noqa: F401  ← reemplazar
    with mock.patch('requests.post') as post:
        post.return_value.status_code = 200
        post.return_value.json.return_value = {'texto': 'ok'}
        mi_modulo.redactar(['cedula', 'carrera'], [[CEDULA, 'Software']])
        cuerpo = str(post.call_args)
    assert CEDULA not in cuerpo
