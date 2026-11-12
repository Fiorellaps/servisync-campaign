"""Genera la serie de posts de Instagram de ServiSync Digital Solutions (SVG + PNG).

Uso:  .venv/bin/python campaign/build.py
Salida: campaign/out/post_N.svg y post_N.png (1080x1080) y story_N.png (1080x1920)
"""
from pathlib import Path

import pymupdf

OUT = Path(__file__).parent / "out"
NAVY, NAVY2, GOLD, WHITE, SOFT, GREEN = "#0B3B5B", "#0F4F78", "#18C2A5", "#FFFFFF", "#C9DCEA", "#22A06B"
FONT = "Helvetica, Arial, sans-serif"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;")


def text(x, y, s, size, fill=WHITE, weight=700, anchor="start", spacing=0):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}" letter-spacing="{spacing}">{esc(s)}</text>')


def check(x, y):
    return (f'<rect x="{x}" y="{y}" width="28" height="28" rx="8" fill="{GREEN}"/>'
            f'<path d="M{x+6} {y+14} l7 7 l11 -13" stroke="#fff" stroke-width="4" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def row(y, label, done=True):
    box = check(48, y + 18) if done else f'<rect x="48" y="{y+18}" width="28" height="28" rx="8" fill="#E3E8F2"/>'
    return f'<rect x="32" y="{y}" width="296" height="64" rx="14" fill="#fff"/>{box}' + text(92, y + 39, label, 21, NAVY, 500)


# ───────── pantallas del móvil (coordenadas locales 336x616 dentro del marco) ─────────
def screen_checklist():
    return (row(152, "Cuadro eléctrico") + row(228, "Toma de tierra") + row(304, "Fotos adjuntas")
            + signature_box(388) + button(532, "Descargar PDF"))


def signature_box(y):
    return (f'<rect x="32" y="{y}" width="296" height="120" rx="14" fill="#fff" stroke="#D5DCEA" stroke-width="2" stroke-dasharray="8 6"/>'
            + text(48, y + 26, "Firma del cliente", 16, "#6B7A99", 500)
            + f'<path d="M62 {y+80} C86 {y+58} 104 {y+106} 126 {y+78} S164 {y+56} 178 {y+86} S226 {y+60} 252 {y+84} S292 {y+70} 304 {y+82}" '
              f'stroke="{NAVY2}" stroke-width="5" fill="none" stroke-linecap="round"/>')


def button(y, label):
    return (f'<rect x="32" y="{y}" width="296" height="64" rx="32" fill="{NAVY}"/>'
            + text(180, y + 41, label, 24, GOLD, 700, "middle"))


def screen_template():
    out = text(32, 160, "12 campos detectados", 22, NAVY, 700)
    for i, (lbl, kind) in enumerate([("Cliente", "Texto"), ("Dirección", "Texto"), ("Potencia (kW)", "Texto"),
                                      ("Conforme", "Casilla"), ("Observaciones", "Multilínea")]):
        y = 184 + i * 62
        out += (f'<rect x="32" y="{y}" width="296" height="52" rx="12" fill="#fff"/>' + check(46, y + 12)
                + text(86, y + 33, lbl, 19, NAVY, 500) + text(316, y + 33, kind, 16, "#6B7A99", 500, "end"))
    return out + button(512, "Crear plantilla")


def screen_photos():
    out = ""
    for i, c in enumerate(["#8FB8E8", "#F2C879", "#9FD3B4", "#C7A8E8", "#F0A8A8", "#A8D8E8"]):
        x, y = 32 + (i % 3) * 102, 152 + (i // 3) * 102
        out += (f'<rect x="{x}" y="{y}" width="92" height="92" rx="14" fill="{c}"/>'
                f'<circle cx="{x+30}" cy="{y+32}" r="10" fill="#fff" opacity="0.7"/>'
                f'<path d="M{x} {y+78} L{x+34} {y+50} L{x+60} {y+72} L{x+92} {y+46} V{y+78} Q{x+92} {y+92} {x+78} {y+92} H{x+14} Q{x} {y+92} {x} {y+78}Z" fill="#fff" opacity="0.5"/>')
    return out + signature_box(372) + button(512, "Guardar")


def screen_versions():
    out = (f'<rect x="32" y="148" width="296" height="52" rx="26" fill="#fff" stroke="#D5DCEA" stroke-width="2"/>'
           f'<circle cx="64" cy="174" r="9" fill="none" stroke="#6B7A99" stroke-width="3"/>'
           f'<path d="M71 181 l8 8" stroke="#6B7A99" stroke-width="3" stroke-linecap="round"/>'
           + text(90, 181, "Revisión Juan Pérez", 19, NAVY, 500))
    for i, (v, note) in enumerate([("v3", "Firmada por el cliente"), ("v2", "Pendiente firma"), ("v1", "Borrador")]):
        y = 220 + i * 84
        out += (f'<rect x="32" y="{y}" width="296" height="72" rx="14" fill="#fff"/>'
                f'<rect x="48" y="{y+20}" width="46" height="32" rx="16" fill="{GOLD if i == 0 else "#E3E8F2"}"/>'
                + text(71, y + 43, v, 18, NAVY, 800, "middle") + text(108, y + 43, note, 19, NAVY, 500))
    return out + button(512, "Abrir versión")


def screen_pdf():
    out = (f'<rect x="72" y="146" width="216" height="290" rx="10" fill="#fff" stroke="#D5DCEA" stroke-width="2"/>'
           + text(88, 176, "PARTE DE TRABAJO", 15, NAVY, 800))
    for i in range(7):
        out += f'<rect x="88" y="{196 + i * 24}" width="{150 if i % 3 else 184}" height="8" rx="4" fill="#E3E8F2"/>'
    out += check(88, 372) + f'<path d="M150 410 C160 384 170 430 184 400 S210 390 220 408" stroke="{NAVY2}" stroke-width="4" fill="none" stroke-linecap="round"/>'
    return out + button(452, "Enviar al cliente") + text(180, 546, "Listo en menos de 5 minutos", 17, "#6B7A99", 500, "middle")


def phone(x, y, title, screen, scale=1.0):
    return (f'<g transform="translate({x},{y}) scale({scale})">'
            f'<rect x="8" y="22" width="360" height="640" rx="44" fill="#000" opacity="0.25"/>'
            f'<rect width="360" height="640" rx="44" fill="#04202F"/>'
            f'<rect x="12" y="12" width="336" height="616" rx="34" fill="#F5F7FB"/>'
            f'<rect x="130" y="24" width="100" height="10" rx="5" fill="#04202F"/>'
            f'<rect x="12" y="52" width="336" height="76" fill="{GOLD}"/>'
            + text(36, 98, title, 26, NAVY, 800)
            + f'<g>{screen}</g></g>')


def logo(x, y):
    mark = (f'<rect width="76" height="76" rx="20" fill="#F4F8FA"/>'
            f''
            f'<g transform="scale(0.2969)"><g fill="none" stroke="{NAVY}" stroke-width="16" stroke-linecap="round">'
            f'<path d="M68 128 A60 60 0 0 1 164 80"/><path d="M188 128 A60 60 0 0 1 92 176"/></g>'
            f'<polygon points="176.8,89.6 172.4,68.8 155.6,91.2" fill="{NAVY}"/>'
            f'<polygon points="79.2,166.4 83.6,187.2 100.4,164.8" fill="{NAVY}"/>'
            f'<circle cx="128" cy="128" r="15" fill="{GOLD}"/></g>')
    name = (f'<text x="96" y="36" font-family="{FONT}" font-size="36" font-weight="800" fill="{WHITE}">Servi'
            f'<tspan fill="{GOLD}">Sync</tspan></text>')
    return (f'<g transform="translate({x},{y})">{mark}{name}'
            + text(96, 64, "DIGITAL SOLUTIONS", 22, SOFT, 400, spacing=4) + "</g>")


def base(h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 {h}" width="1080" height="{h}">'
            f'<rect width="1080" height="{h}" fill="{NAVY}"/>'
            f'<circle cx="930" cy="170" r="260" fill="{GOLD}" opacity="0.07"/>'
            f'<circle cx="120" cy="{h-100}" r="220" fill="{GOLD}" opacity="0.06"/>{body}</svg>')


POSTS = [
    dict(lines=["Tus partes de", "trabajo, sin papeles."], sub="Rellena, firma y envía en minutos.",
         bullets=["Plantillas a tu medida", "Fotos y firma digital", "Historial de versiones", "PDF listo para enviar"],
         title="Revisión instalación", screen=screen_checklist, cta="Pruébalo gratis"),
    dict(lines=["Tu PDF se convierte", "en formulario."], sub="Sube tu plantilla y empieza a rellenar.",
         bullets=["Sube un PDF rellenable", "Detectamos los campos solos", "Ajusta etiquetas y tipos", "Úsalo desde el móvil"],
         title="Nueva plantilla", screen=screen_template, cta="Sube tu plantilla"),
    dict(lines=["Fotos y firma,", "en el sitio."], sub="El cliente conforme antes de irte.",
         bullets=["Fotos desde la cámara", "Firma con el dedo", "Descarga todo en ZIP", "Sin volver a la oficina"],
         title="Fotos y firma", screen=screen_photos, cta="Pruébalo gratis"),
    dict(lines=["Nada se pierde.", "Todo se encuentra."], sub="Cada cambio queda guardado.",
         bullets=["Versiones con notas", "Vuelve a cualquier punto", "Búsqueda en vivo", "Partes siempre a mano"],
         title="Historial", screen=screen_versions, cta="Organiza tus partes"),
    dict(lines=["Digitaliza tus partes", "hoy mismo."], sub="PDF profesional, listo para enviar.",
         bullets=["Vista previa del PDF", "Descarga con un toque", "Menos papel, más trabajo", "Para profesionales de servicios"],
         title="Parte listo", screen=screen_pdf, cta="Solicita tu demo"),
]


def post_svg(p) -> str:
    b = logo(80, 80)
    b += text(80, 290, p["lines"][0], 78, WHITE, 800) + text(80, 378, p["lines"][1], 78, GOLD, 800)
    b += text(80, 446, p["sub"], 32, SOFT, 400)
    b += phone(655, 440, p["title"], p["screen"](), 0.92)
    for i, s in enumerate(p["bullets"]):
        y = 571 + i * 70
        b += f'<circle cx="96" cy="{y-11}" r="14" fill="{GOLD}"/>' + text(126, y, s, 30, WHITE, 600)
    b += f'<rect x="80" y="880" width="420" height="88" rx="44" fill="{GOLD}"/>' + text(290, 936, p["cta"], 32, NAVY, 800, "middle")
    b += text(80, 1030, "Para electricistas y profesionales de servicios", 24, "#8FB5CC", 400)
    return base(1080, b)


def story_svg(p) -> str:
    b = logo(80, 120)
    b += text(80, 380, p["lines"][0], 80, WHITE, 800) + text(80, 470, p["lines"][1], 80, GOLD, 800)
    b += text(80, 540, p["sub"], 34, SOFT, 400)
    b += phone(324, 620, p["title"], p["screen"](), 1.2)
    b += f'<rect x="160" y="1470" width="760" height="100" rx="50" fill="{GOLD}"/>' + text(540, 1535, p["cta"], 38, NAVY, 800, "middle")
    b += text(540, 1660, "Para electricistas y profesionales de servicios", 26, "#8FB5CC", 400, "middle")
    return base(1920, b)


def render(svg: str, path: Path) -> None:
    path.with_suffix(".svg").write_text(svg, encoding="utf-8")
    with pymupdf.open(stream=svg.encode(), filetype="svg") as doc:
        pdf = pymupdf.open("pdf", doc.convert_to_pdf())
        pdf[0].get_pixmap(dpi=72).save(path.with_suffix(".png"))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for i, p in enumerate(POSTS, 1):
        render(post_svg(p), OUT / f"post_{i}")
        render(story_svg(p), OUT / f"story_{i}")
    print("OK", sorted(f.name for f in OUT.glob("*.png")))
