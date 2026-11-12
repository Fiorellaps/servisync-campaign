"""Landing page de ServiSync Digital Solutions con formulario de contacto en Supabase.

Ejecutar desde esta carpeta (para que lea .streamlit/ de aquí):
    cd landing && streamlit run app.py
"""
from __future__ import annotations

import base64
import re
import time
from html import escape
from pathlib import Path

import requests
import streamlit as st

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent  # campaign/
NAVY, TEAL, BG = "#0B3B5B", "#18C2A5", "#F4F8FA"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SECTORES = ["Electricidad", "Fontanería", "Climatización", "Telecomunicaciones", "Mantenimiento", "Otro"]
COOLDOWN_S = 30  # evita envíos repetidos desde la misma sesión

st.set_page_config(page_title="ServiSync · Partes de trabajo sin papeles", page_icon=str(ASSETS / "logo/servisync-icon.svg"),
                   layout="wide", initial_sidebar_state="collapsed")


# ───────────────────────── Supabase ─────────────────────────
def supabase_cfg() -> dict | None:
    try:
        cfg = st.secrets["supabase"]
        return {"url": cfg["url"].rstrip("/"), "key": cfg["key"], "table": cfg.get("table", "contactos")}
    except Exception:  # sin secrets.toml o sin la sección [supabase]
        return None


def save_contact(cfg: dict, row: dict) -> None:
    """Inserta vía la API REST de Supabase. La clave pública solo puede insertar (ver schema.sql)."""
    r = requests.post(
        f"{cfg['url']}/rest/v1/{cfg['table']}", json=row, timeout=10,
        headers={"apikey": cfg["key"], "Content-Type": "application/json", "Prefer": "return=minimal"},
    )
    r.raise_for_status()


# ───────────────────────── estilos ─────────────────────────
st.html(f"""<style>
header[data-testid="stHeader"], #MainMenu, footer {{display:none}}
.block-container {{max-width:1120px; padding-top:1.5rem; padding-bottom:3rem}}
.ss h1 {{font-size:3.2rem; line-height:1.08; font-weight:800; color:{NAVY}; margin:.4rem 0 1rem}}
.ss h1 span, .ss .accent {{color:{TEAL}}}
.ss h2 {{font-size:2rem; font-weight:800; color:{NAVY}; margin:0 0 .4rem}}
.ss .lead {{font-size:1.2rem; color:#41566A; margin-bottom:1.6rem}}
.ss .eyebrow {{font-size:.8rem; letter-spacing:.18em; font-weight:700; color:{TEAL}; text-transform:uppercase}}
.ss .cta {{display:inline-block; background:{TEAL}; color:{NAVY}!important; font-weight:800; padding:.85rem 1.8rem;
          border-radius:999px; text-decoration:none!important; margin-right:.6rem}}
.ss .cta.ghost {{background:transparent; border:2px solid {NAVY}; color:{NAVY}!important}}
.ss .nav {{display:flex; justify-content:space-between; align-items:center; margin-bottom:2rem}}
.ss .nav a.cta {{padding:.55rem 1.3rem}}
.ss .grid {{display:grid; grid-template-columns:repeat(3,1fr); gap:1.1rem; margin-top:1.4rem}}
.ss .card {{background:#fff; border:1px solid #DDE6EC; border-radius:18px; padding:1.4rem}}
.ss .card .ic {{font-size:1.7rem}}
.ss .card h3 {{font-size:1.1rem; color:{NAVY}; margin:.5rem 0 .3rem}}
.ss .card p {{color:#5B6B7A; margin:0; font-size:.97rem}}
.ss .feats {{gap:1.5rem}}
.ss .feat {{background:#fff; border:1px solid #DDE6EC; border-radius:20px; overflow:hidden;
           box-shadow:0 1px 2px rgba(11,59,91,.04); transition:transform .2s ease, box-shadow .2s ease}}
.ss .feat:hover {{transform:translateY(-4px); box-shadow:0 18px 40px rgba(11,59,91,.12)}}
.ss .feat img {{display:block; width:100%; aspect-ratio:8/5; object-fit:cover; border-bottom:1px solid #E6EEF3}}
.ss .feat-body {{padding:1.3rem 1.4rem 1.5rem}}
.ss .feat .tag {{display:inline-block; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase;
                color:#0E8F7A; background:#E6F7F4; padding:.25rem .6rem; border-radius:999px}}
.ss .feat h3 {{font-size:1.12rem; line-height:1.3; color:{NAVY}; margin:.7rem 0 .4rem}}
.ss .feat p {{color:#5B6B7A; margin:0; font-size:.95rem; line-height:1.55}}
@media (max-width: 1000px) and (min-width: 801px) {{ .ss .feats {{grid-template-columns:repeat(2,1fr)}} }}
.ss .step {{font-size:2.4rem; font-weight:800; color:{TEAL}}}
.ss .band {{background:{NAVY}; color:#fff; border-radius:24px; padding:2.2rem 2.4rem; margin:3rem 0 2rem}}
.ss .band h2 {{color:#fff}} .ss .band p {{color:#C7D6E0; margin:0}}
.ss .foot {{text-align:center; color:#7A8A99; font-size:.9rem; margin-top:3rem}}
[data-testid="stVideo"], .st-key-hero_media img {{max-width:340px; margin:0 auto; display:block;
  border-radius:24px; box-shadow:0 24px 48px rgba(11,59,91,.25)}}
.st-key-contact_card {{background:#fff; border:1px solid #DDE6EC; border-radius:24px; padding:1.6rem}}
@media (max-width: 800px) {{ .ss h1 {{font-size:2.3rem}} .ss .grid {{grid-template-columns:1fr}} }}
</style>""")


def html(body: str) -> None:
    st.html(f'<div class="ss">{body}</div>')


# ───────────────────────── cabecera y hero ─────────────────────────
logo_b64 = base64.b64encode((ASSETS / "logo/servisync-logo.svg").read_bytes()).decode()
html(f'<div class="nav"><img src="data:image/svg+xml;base64,{logo_b64}" alt="ServiSync Digital Solutions" '
     f'style="height:60px;width:auto"><a class="cta" href="#contacto">Solicita tu demo</a></div>')

left, right = st.columns([1.15, 1], gap="large", vertical_alignment="center")
with left:
    html("""
      <div class="eyebrow">Para electricistas y profesionales de servicios</div>
      <h1>Tus partes de trabajo, <span>sin papeles.</span></h1>
      <p class="lead">Rellena el parte desde el móvil, adjunta fotos, recoge la firma del cliente
      y envía un PDF profesional antes de salir de la obra.</p>
      <a class="cta" href="#contacto">Quiero probarlo</a><a class="cta ghost" href="#funciones">Ver funciones</a>
    """)
with right, st.container(key="hero_media"):
    reel = ASSETS / "out/servisync_reel_sin_audio.mp4"  # sin pista de audio: los navegadores solo permiten autoplay en silencio
    if reel.exists():
        st.video(str(reel), loop=True, autoplay=True, muted=True)
    else:
        st.image(str(ASSETS / "out/post_1.png"), use_container_width=True)

# ───────────────────────── funciones ─────────────────────────
FEATURES = [  # (imagen en assets/, etiqueta, título, descripción) · imágenes generadas con make_features.py
    ("plantillas", "Plantillas", "Tu plantilla, convertida en formulario",
     "Sube el PDF rellenable que ya usas. ServiSync detecta sus campos y genera el formulario automáticamente."),
    ("firma", "Firma digital", "Conformidad del cliente en el sitio",
     "Técnico y cliente firman en la pantalla con nombre y DNI. La firma se estampa en el PDF."),
    ("fotos", "Evidencias", "Fotos del trabajo realizado",
     "Captura con la cámara o sube desde la galería. Cada foto queda unida al parte y se descarga en ZIP."),
    ("versiones", "Trazabilidad", "Historial completo de versiones",
     "Cada guardado genera una versión con su nota. Consulta o recupera cualquier estado anterior."),
    ("busqueda", "Organización", "Encuentra cualquier parte al instante",
     "Búsqueda en tiempo real por nombre del parte o por las notas de sus versiones."),
    ("pdf", "Entrega", "PDF profesional, listo para enviar",
     "Revisa la vista previa y descarga el parte relleno con tu formato de siempre."),
]


@st.cache_data
def _img_uri(path: str, mtime: float) -> str:  # sin «_»: Streamlit no hashea los argumentos con guion bajo
    return "data:image/png;base64," + base64.b64encode(Path(path).read_bytes()).decode()


def img_uri(name: str) -> str:
    path = HERE / f"assets/feat_{name}.png"
    return _img_uri(str(path), path.stat().st_mtime)  # la fecha invalida la caché si se regeneran las imágenes


cards = "".join(
    f'<article class="feat"><img src="{img_uri(img)}" alt="{escape(title)}" loading="lazy">'
    f'<div class="feat-body"><span class="tag">{tag}</span><h3>{title}</h3><p>{desc}</p></div></article>'
    for img, tag, title, desc in FEATURES
)
st.html('<div id="funciones"></div>')
html(f'<div style="margin-top:4rem"><div class="eyebrow">Funciones</div><h2>Todo el parte, en tu bolsillo</h2>'
     f'<p class="lead" style="max-width:640px">Las herramientas que necesita un técnico de campo para cerrar '
     f'cada intervención con un parte completo, firmado y documentado.</p>'
     f'<div class="grid feats">{cards}</div></div>')

# ───────────────────────── cómo funciona ─────────────────────────
STEPS = [
    ("1", "Elige el modelo", "Usa un modelo existente o sube la plantilla PDF que ya usas."),
    ("2", "Rellena en el sitio", "Marca las comprobaciones, añade medidas, fotos y la firma del cliente."),
    ("3", "Envía el PDF", "Descarga el parte relleno y envíalo. Queda guardado con su historial."),
]
steps = "".join(f'<div class="card"><div class="step">{n}</div><h3>{t}</h3><p>{d}</p></div>' for n, t, d in STEPS)
html(f'<div style="margin-top:3.5rem"><div class="eyebrow">Cómo funciona</div><h2>Tres pasos y listo</h2>'
     f'<div class="grid">{steps}</div></div>')

html("""<div class="band"><h2>Menos papeleo, más tiempo para trabajar.</h2>
     <p>Deja de pasar partes a limpio por la noche. ServiSync los deja listos en la obra.</p></div>""")

# ───────────────────────── formulario de contacto ─────────────────────────
st.html('<div id="contacto"></div>')
info, form_col = st.columns([1, 1.3], gap="large")
with info:
    html("""<div class="eyebrow">Contacto</div><h2>Solicita tu demo</h2>
      <p class="lead">Déjanos tus datos y te enseñamos ServiSync con tus propias plantillas.</p>
      <div class="card"><h3>Qué incluye la demo</h3>
      <p>✔ Configuración de tu plantilla de parte<br>✔ Prueba en tu móvil<br>✔ Sin compromiso</p></div>""")

cfg = supabase_cfg()
with form_col, st.container(key="contact_card"):
    if st.session_state.get("contact_ok"):
        st.success("¡Gracias! Hemos recibido tus datos y te contactaremos pronto.")
        if st.button("Enviar otra solicitud"):
            st.session_state.pop("contact_ok")
            st.rerun()
    else:
        if cfg is None:
            st.warning("Formulario sin configurar: falta la sección [supabase] en .streamlit/secrets.toml.")
        with st.form("contact", clear_on_submit=False, border=False):
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre y apellidos *", max_chars=100)
            empresa = c2.text_input("Empresa", max_chars=120)
            email = c1.text_input("Email *", max_chars=200)
            telefono = c2.text_input("Teléfono", max_chars=30)
            sector = st.selectbox("Sector", SECTORES, index=None, placeholder="Elige tu sector")
            mensaje = st.text_area("¿Qué necesitas?", max_chars=2000, height=110,
                                   placeholder="p. ej. Hacemos revisiones de aerotermia y queremos digitalizar el checklist")
            acepta = st.checkbox("Acepto que ServiSync use estos datos para contactarme sobre el servicio. *")
            sent = st.form_submit_button("Enviar solicitud", type="primary", use_container_width=True,
                                         disabled=cfg is None)

        if sent:
            nombre, email = nombre.strip(), email.strip().lower()
            errors = []
            if len(nombre) < 2:
                errors.append("Indica tu nombre.")
            if not EMAIL_RE.match(email):
                errors.append("Indica un email válido.")
            if not acepta:
                errors.append("Debes aceptar el uso de tus datos para que podamos contactarte.")
            wait = COOLDOWN_S - (time.time() - st.session_state.get("last_sent", 0))
            if wait > 0:
                errors.append(f"Espera {int(wait) + 1} s antes de enviar otra solicitud.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                row = {"nombre": nombre, "email": email, "telefono": telefono.strip() or None,
                       "empresa": empresa.strip() or None, "sector": sector, "mensaje": mensaje.strip() or None,
                       "acepta_privacidad": True, "origen": st.query_params.get("utm_source", "landing")[:40]}
                try:
                    save_contact(cfg, row)
                except requests.RequestException:
                    st.error("No hemos podido enviar tu solicitud. Inténtalo de nuevo en unos minutos.")
                else:
                    st.session_state["last_sent"] = time.time()
                    st.session_state["contact_ok"] = True
                    st.rerun()

html(f'<div class="foot">© ServiSync <span class="accent">Digital Solutions</span> · '
     f'{escape("Partes de trabajo digitales para profesionales de servicios")}</div>')
