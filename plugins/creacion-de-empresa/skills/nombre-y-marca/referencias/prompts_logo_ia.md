# Prompts para explorar el logo con un generador de imágenes

Sustituye `[NOMBRE]`, `[ACENTO]` (hex del color de marca) y `[FONDO]` (hex del fondo oscuro) con los valores de `empresa.json → marca`. Son para **explorar**: el logo definitivo lo entrega un diseñador en vector.

## Reglas para que salga bien
1. Pide símbolo y nombre **juntos** como un lockup terminado, con tipografía real.
2. Pide **fondo transparente**. Si no puede, fondo sólido liso para recortarlo después.
3. Pide **logo plano tipo vector**, sin sombras, sin degradados fotorrealistas, sin 3D, sin mockup.
4. **Una sola propuesta por imagen**, a tamaño completo; si devuelve un panel con varias, repite pidiendo una sola.
5. Da los **hex** de la paleta, no solo nombres de color.
6. Prohíbe los clichés del sector (en IA: cerebros, circuitos, robots) y el círculo genérico con una inicial.
7. **Revisa cada letra** del resultado: los textos salen con errores.

## Prompt 1 · Logo principal
```
Diseña un logo corporativo completo para "[NOMBRE]", [una frase de qué hace la empresa]. Diseño profesional y elegante, al nivel de una consultora de prestigio, no una plantilla de generador automático.
Genera UNA SOLA propuesta a tamaño completo, no varias miniaturas ni un panel comparativo.
Lockup limpio y equilibrado: (1) un símbolo/monograma construido a partir de la inicial de [NOMBRE] con trazos geométricos limpios y uso inteligente del espacio negativo; (2) el texto "[NOMBRE]" en mayúsculas, tipografía sans-serif geométrica, espaciado amplio y nítido.
Color: [ACENTO] sólido. Fondo transparente (PNG con alfa); si no es posible, fondo sólido [FONDO] liso.
Logo plano tipo vector, sin sombras, sin degradados fotorrealistas, sin efecto 3D, sin mockup.
```

## Prompt 2 · Monocromo (sello e impresión de una tinta)
```
Mismo logo de [NOMBRE] (mismo diseño y tipografía), en un solo color: negro sólido puro sobre fondo blanco liso. Debe seguir legible reducido a 2–3 cm. Plano, sin sombras ni degradados.
```

## Prompt 3 · Blanco (fondos oscuros)
```
Mismo logo de [NOMBRE], en blanco puro sobre fondo [FONDO] liso. Plano, sin sombras ni degradados.
```

## Prompt 4 · Símbolo solo
```
Solo el símbolo del logo de [NOMBRE], sin texto, centrado, en [ACENTO] sobre fondo transparente. Debe leerse a 16 px (favicon) y en bordado de gorra: trazos gruesos, sin detalles finos.
```

## Prompt 5 · Sello circular (papelería y uso comercial)
```
Sello circular corporativo clásico, en negro puro, con anillo grueso en el borde: arriba "[NOMBRE]" curvado, abajo "[CIUDAD] · [PAÍS]", y al centro el símbolo del logo. Una sola propuesta a tamaño completo, fondo blanco liso, sin degradados.
```

## Portadas de redes (opcional)
Las portadas se generan sin IA con `logos-y-piezas/scripts/exportar_logo.py` a partir del logo final: Facebook 820×312, LinkedIn 1584×396, YouTube 2560×1440 (zona segura central), vista previa del enlace 1200×630. Es más fiel al logo y evita errores de texto.

## Después de generar
Elige 1–2 variantes, pide el vector al diseñador (o encárgalo con `plantillas/brief_disenador.md`), y pasa el archivo a la skill `logos-y-piezas`.
