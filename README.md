# ServiSync Digital Solutions · Campaña

Material de lanzamiento de ServiSync, la app de partes de trabajo digitales para electricistas y profesionales de servicios.

| Carpeta / archivo | Contenido |
|---|---|
| `landing/` | Landing page en Streamlit con formulario de contacto que se envía por email |
| `out/` | Posts (1080×1080), stories (1080×1920) y reel de Instagram |
| `logo/` | Logo e icono en SVG |
| `voz/` | Guion y locución del reel |
| `build.py` | Genera los posts y stories |
| `video.py` | Genera el reel a partir de las stories y la locución |

## Landing

```bash
pip install -r landing/requirements.txt
cd landing && streamlit run app.py
```

Cada solicitud del formulario llega como correo a `cloud.ai.champions@gmail.com`. Al pulsar «Responder» se contesta directamente al interesado.

Para activar el formulario:

1. En la cuenta de Gmail, activa la verificación en dos pasos y crea una contraseña de aplicación en <https://myaccount.google.com/apppasswords>.
2. Copia `landing/.streamlit/secrets.toml.example` a `landing/.streamlit/secrets.toml` y pega esa contraseña en `password`. Este archivo no se sube a git.

El campo «Origen» del correo muestra el `utm_source` del enlace, p. ej. `?utm_source=instagram`.

## Regenerar imágenes y vídeo

```bash
pip install pymupdf
python build.py                  # posts y stories en out/
python landing/make_features.py  # ilustraciones de la sección Funciones
python video.py                  # reel (requiere ffmpeg y macOS para la voz sintética)
```

## Licencia

El código está bajo licencia [MIT](LICENSE). La marca ServiSync, el logo, las imágenes, los vídeos y las grabaciones de voz no están incluidos en esa licencia: todos los derechos reservados (ver [BRAND-NOTICE.md](BRAND-NOTICE.md)).
