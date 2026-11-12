"""Landing page de ServiSync Digital Solutions con formulario de contacto que se envía por email (SMTP).

Ejecutar desde esta carpeta (para que lea .streamlit/ de aquí):
    cd landing && streamlit run app.py
"""
from __future__ import annotations

import base64
import re
import smtplib
import ssl
import time
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr
from html import escape
from pathlib import Path

import streamlit as st

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent  # campaign/
NAVY, TEAL, BG = "#0B3B5B", "#18C2A5", "#F4F8FA"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SECTORES = ["Electricidad", "Fontanería", "Climatización", "Telecomunicaciones", "Mantenimiento", "Otro"]
COOLDOWN_S = 30  # evita envíos repetidos desde la misma sesión

# Datos del responsable del tratamiento para la política de privacidad (privacidad.md).
# Completa los campos entre corchetes antes de publicar la web.
PRIVACY = {
    "version": "12/11/2026",  # cámbiala al modificar privacidad.md: queda registrada en cada solicitud
    "titular": "[Nombre y apellidos o razón social]",
    "nif": "[NIF / CIF]",
    "direccion": "[Dirección postal completa]",
    "email": "cloud.ai.champions@gmail.com",
}
PRIVACY_URL = "?p=privacidad"

# Redes sociales: (nombre, usuario, URL, trazado SVG del icono en una caja de 24x24)
SOCIAL = [
    ("Instagram", "@servisync.ds", "https://www.instagram.com/servisync.ds/",
     '<rect x="2.5" y="2.5" width="19" height="19" rx="5.5" fill="none" stroke="{c}" stroke-width="2.2"/>'
     '<circle cx="12" cy="12" r="4.3" fill="none" stroke="{c}" stroke-width="2.2"/>'
     '<circle cx="17.4" cy="6.6" r="1.4" fill="{c}"/>'),
    ("TikTok", "@servisync.ds", "https://www.tiktok.com/@servisync.ds",
     '<path fill="{c}" d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 '
     '1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 '
     '3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49'
     '.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63'
     '.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4'
     '-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>'),
]

st.set_page_config(page_title="ServiSync · Partes de trabajo sin papeles", page_icon=str(ASSETS / "logo/servisync-icon.svg"),
                   layout="wide", initial_sidebar_state="collapsed")


# ───────────────────────── SMTP ─────────────────────────
def smtp_cfg() -> dict | None:
    try:
        c = st.secrets["smtp"]
        user = c["user"]
        return {"host": c.get("host", "smtp.gmail.com"), "port": int(c.get("port", 465)), "user": user,
                "password": c["password"], "to": c.get("to", user)}
    except Exception:  # sin secrets.toml o sin la sección [smtp]
        return None


def one_line(s: str) -> str:
    """Quita saltos de línea para que un valor del usuario no pueda inyectar cabeceras en el correo."""
    return re.sub(r"[\r\n]+", " ", s).strip()


def send_contact(cfg: dict, row: dict) -> None:
    """Envía la solicitud al buzón de ServiSync. «Responder» contesta directamente al interesado."""
    labels = [("Nombre", "nombre"), ("Email", "email"), ("Teléfono", "telefono"), ("Empresa", "empresa"),
              ("Sector", "sector"), ("Origen", "origen"), ("Política de privacidad aceptada", "acepta_privacidad")]
    lines = [f"{lbl}: {row[k] if row[k] not in (None, '') else '—'}" for lbl, k in labels]
    body = ("Nueva solicitud de demo desde la landing de ServiSync\n"
            f"Fecha: {datetime.now():%d/%m/%Y %H:%M}\n\n" + "\n".join(lines)
            + f"\n\nMensaje:\n{row['mensaje'] or '—'}\n")

    msg = EmailMessage()
    msg["Subject"] = one_line(f"Solicitud de demo · {row['nombre']}" + (f" ({row['empresa']})" if row["empresa"] else ""))
    msg["From"] = formataddr(("ServiSync Landing", cfg["user"]))
    msg["To"] = cfg["to"]
    msg["Reply-To"] = formataddr((one_line(row["nombre"]), row["email"]))
    msg.set_content(body)

    with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=ssl.create_default_context(), timeout=15) as s:
        s.login(cfg["user"], cfg["password"])
        s.send_message(msg)


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
.ss .social {{display:flex; gap:.6rem; flex-wrap:wrap}}
.ss .foot .social {{justify-content:center; margin-bottom:.9rem}}
.ss .social a {{display:inline-flex; align-items:center; gap:.5rem; padding:.5rem .95rem; border-radius:999px;
               background:#fff; border:1px solid #DDE6EC; color:{NAVY}!important; font-weight:600; font-size:.92rem;
               text-decoration:none!important; transition:border-color .15s, box-shadow .15s}}
.ss .social a:hover {{border-color:{TEAL}; box-shadow:0 6px 16px rgba(11,59,91,.10)}}
.ss .social img {{width:18px; height:18px; display:block}}
[data-testid="stVideo"], .st-key-hero_media img {{max-width:340px; margin:0 auto; display:block;
  border-radius:24px; box-shadow:0 24px 48px rgba(11,59,91,.25)}}
.st-key-privacy_card {{background:#fff; border:1px solid #DDE6EC; border-radius:24px; padding:2rem 2.4rem}}
.st-key-privacy_card h1 {{color:{NAVY}; font-size:2.2rem}} .st-key-privacy_card h2 {{color:{NAVY}; font-size:1.25rem; margin-top:1.2rem}}
.st-key-contact_card {{background:#fff; border:1px solid #DDE6EC; border-radius:24px; padding:1.6rem}}
@media (max-width: 800px) {{ .ss h1 {{font-size:2.3rem}} .ss .grid {{grid-template-columns:1fr}} }}
</style>""")


def html(body: str) -> None:
    st.html(f'<div class="ss">{body}</div>')


def social_links() -> str:
    links = []
    for name, handle, url, icon in SOCIAL:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">{icon.format(c=NAVY)}</svg>'
        src = "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()
        links.append(f'<a href="{url}" target="_blank" rel="noopener noreferrer" aria-label="{name} {handle}">'
                     f'<img src="{src}" alt="">{name} · {handle}</a>')
    return f'<div class="social">{"".join(links)}</div>'


def footer(extra: str = "") -> None:
    html(f'<div class="foot">{social_links()}© ServiSync <span class="accent">Digital Solutions</span>{extra}</div>')


def nav(cta_href: str, cta_label: str) -> None:
    logo_b64 = base64.b64encode((ASSETS / "logo/servisync-logo.svg").read_bytes()).decode()
    html(f'<div class="nav"><a href="./"><img src="data:image/svg+xml;base64,{logo_b64}" '
         f'alt="ServiSync Digital Solutions" style="height:60px;width:auto"></a>'
         f'<a class="cta" href="{cta_href}" target="_self">{cta_label}</a></div>')


# ───────────────────────── página: política de privacidad ─────────────────────────
if st.query_params.get("p") == "privacidad":
    nav("./#contacto", "← Volver al formulario")
    _, mid, _ = st.columns([1, 6, 1])
    with mid, st.container(key="privacy_card"):
        st.markdown((HERE / "privacidad.md").read_text(encoding="utf-8").format(**PRIVACY))
    footer()
    st.stop()


# ───────────────────────── cabecera y hero ─────────────────────────
nav("#contacto", "Solicita tu demo")

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
      <p>✔ Configuración de tu plantilla de parte<br>✔ Prueba en tu móvil<br>✔ Sin compromiso</p></div>"""
         f'<h3 style="color:{NAVY}; font-size:1.05rem; margin:1.6rem 0 .7rem">Síguenos</h3>{social_links()}')

cfg = smtp_cfg()
with form_col, st.container(key="contact_card"):
    if st.session_state.get("contact_ok"):
        st.success("¡Gracias! Hemos recibido tus datos y te contactaremos pronto.")
        if st.button("Enviar otra solicitud"):
            st.session_state.pop("contact_ok")
            st.rerun()
    else:
        if cfg is None:
            st.warning("Formulario sin configurar: falta la sección [smtp] en .streamlit/secrets.toml.")
        with st.form("contact", clear_on_submit=False, border=False):
            c1, c2 = st.columns(2)
            nombre = c1.text_input("Nombre y apellidos *", max_chars=100)
            empresa = c2.text_input("Empresa", max_chars=120)
            email = c1.text_input("Email *", max_chars=200)
            telefono = c2.text_input("Teléfono", max_chars=30)
            sector = st.selectbox("Sector", SECTORES, index=None, placeholder="Elige tu sector")
            mensaje = st.text_area("¿Qué necesitas?", max_chars=2000, height=110,
                                   placeholder="p. ej. Hacemos revisiones de aerotermia y queremos digitalizar el checklist")
            st.caption(
                "**Información básica sobre protección de datos.** Responsable: ServiSync Digital Solutions. "
                "Finalidad: responder a tu solicitud y contactarte sobre el servicio. Legitimación: tu consentimiento. "
                "Destinatarios: no se ceden datos a terceros, salvo proveedores necesarios (Google, para el correo). "
                "Derechos: acceso, rectificación, supresión y otros, como se explica en la "
                f"[política de privacidad]({PRIVACY_URL})."
            )
            # Sin enlace en la etiqueta: Streamlit usa el clic en la etiqueta para marcar la casilla y no abre el enlace
            acepta = st.checkbox("He leído y acepto la política de privacidad. *")
            st.markdown(f"[Leer la política de privacidad ↗]({PRIVACY_URL})")
            sent = st.form_submit_button("Enviar solicitud", type="primary", use_container_width=True,
                                         disabled=cfg is None)

        if sent:
            nombre, email = one_line(nombre), one_line(email).lower()
            empresa, telefono = one_line(empresa), one_line(telefono)
            errors = []
            if len(nombre) < 2:
                errors.append("Indica tu nombre.")
            if not EMAIL_RE.match(email):
                errors.append("Indica un email válido.")
            if not acepta:
                errors.append("Debes aceptar la política de privacidad para enviar la solicitud.")
            wait = COOLDOWN_S - (time.time() - st.session_state.get("last_sent", 0))
            if wait > 0:
                errors.append(f"Espera {int(wait) + 1} s antes de enviar otra solicitud.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                row = {"nombre": nombre, "email": email, "telefono": telefono.strip() or None,
                       "empresa": empresa.strip() or None, "sector": sector, "mensaje": mensaje.strip() or None,
                       "acepta_privacidad": f"Sí, el {datetime.now():%d/%m/%Y a las %H:%M} "
                                            f"(política del {PRIVACY['version']})",
                       "origen": st.query_params.get("utm_source", "landing")[:40]}
                try:
                    send_contact(cfg, row)
                except (smtplib.SMTPException, OSError):  # credenciales, red o servidor caído
                    st.error("No hemos podido enviar tu solicitud. Inténtalo de nuevo en unos minutos.")
                else:
                    st.session_state["last_sent"] = time.time()
                    st.session_state["contact_ok"] = True
                    st.rerun()

footer(f' · {escape("Partes de trabajo digitales para profesionales de servicios")}')
