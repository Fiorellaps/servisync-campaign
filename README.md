# ServiSync Digital Solutions · Campaña

Material de lanzamiento de ServiSync, la app de partes de trabajo digitales para electricistas y profesionales de servicios.

| Carpeta / archivo | Contenido |
|---|---|
| `landing/` | Landing page en Streamlit con formulario de contacto que guarda en Supabase |
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

Para activar el formulario:

1. En Supabase, abre **SQL Editor** y ejecuta `landing/schema.sql`. Crea la tabla `contactos`; la clave pública solo puede insertar.
2. Copia `landing/.streamlit/secrets.toml.example` a `landing/.streamlit/secrets.toml` y rellena la URL y la clave pública (anon o publishable). Nunca uses la clave `service_role`.

El campo `origen` guarda el `utm_source` del enlace, p. ej. `?utm_source=instagram`.

## Regenerar imágenes y vídeo

```bash
pip install pymupdf
python build.py                  # posts y stories en out/
python landing/make_features.py  # ilustraciones de la sección Funciones
python video.py                  # reel (requiere ffmpeg y macOS para la voz sintética)
```

## Licencia

El código está bajo licencia [MIT](LICENSE). La marca ServiSync, el logo, las imágenes, los vídeos y las grabaciones de voz no están incluidos en esa licencia: todos los derechos reservados.
