"""Genera las ilustraciones de la sección «Funciones» de la landing (PNG a 2x).

Uso:  python landing/make_features.py
Salida: landing/assets/feat_<id>.png (1600x1000)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # campaign/ para reutilizar build.py

import pymupdf  # noqa: E402

from build import (GOLD as TEAL, NAVY, NAVY2, button, check, phone, screen_pdf, screen_photos,  # noqa: E402
                   screen_template, screen_versions, signature_box, text)

W, H = 800, 500
GREY = "#6B7A99"


def field(y, label, value):
    return (text(32, y, label, 15, GREY, 600)
            + f'<rect x="32" y="{y+10}" width="296" height="50" rx="12" fill="#fff" stroke="#D5DCEA" stroke-width="2"/>'
            + text(48, y + 42, value, 19, NAVY, 500))


def screen_signature():
    return (field(160, "Nombre y apellidos", "Juan Pérez García") + field(240, "DNI", "12345678Z")
            + signature_box(330) + button(472, "Guardar firma"))


def screen_search():
    out = (f'<rect x="32" y="148" width="296" height="52" rx="26" fill="#fff" stroke="{TEAL}" stroke-width="3"/>'
           f'<circle cx="64" cy="172" r="9" fill="none" stroke="{NAVY}" stroke-width="3"/>'
           f'<path d="M71 179 l8 8" stroke="{NAVY}" stroke-width="3" stroke-linecap="round"/>'
           + text(90, 181, "aerotermia", 19, NAVY, 500)
           + f'<rect x="210" y="164" width="2" height="24" fill="{NAVY}"/>'
           + text(32, 234, "3 de 24 partes", 15, GREY, 600))
    for i, (t, meta) in enumerate([("Aerotermia · Calle Mayor 4", "v3 · 12/11"), ("Revisión aerotermia Ruiz", "v1 · 08/11"),
                                   ("Aerotermia nave industrial", "v2 · 02/11")]):
        y = 250 + i * 78
        out += (f'<rect x="32" y="{y}" width="296" height="66" rx="14" fill="#fff"/>'
                f'<rect x="46" y="{y+16}" width="34" height="34" rx="9" fill="#E6F7F4"/>'
                f'<path d="M56 {y+24} h10 l6 6 v14 h-16 z" fill="none" stroke="{TEAL}" stroke-width="2.5" stroke-linejoin="round"/>'
                + text(92, y + 30, t, 16, NAVY, 700) + text(92, y + 52, meta, 14, GREY, 500))
    return out


FEATURES = {
    "plantillas": ("Nueva plantilla", screen_template),
    "firma": ("Firma del cliente", screen_signature),
    "fotos": ("Fotos y firma", screen_photos),
    "versiones": ("Historial", screen_versions),
    "busqueda": ("Partes guardados", screen_search),
    "pdf": ("Parte listo", screen_pdf),
}


def scene(title, screen) -> str:
    # Fondo suave con el móvil saliendo desde abajo, recortado por el borde
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="#E8F3F2"/>'  # MuPDF no pinta degradados: color sólido
            f'<circle cx="{W-70}" cy="70" r="150" fill="{TEAL}" opacity="0.10"/>'
            f'<circle cx="60" cy="{H-30}" r="130" fill="{NAVY2}" opacity="0.06"/>'
            + phone(W / 2 - 162, 48, title, screen(), 0.9)
            + "</svg>")


def render(svg: str, path: Path) -> None:
    with pymupdf.open(stream=svg.encode(), filetype="svg") as doc:
        pdf = pymupdf.open("pdf", doc.convert_to_pdf())
        pdf[0].get_pixmap(dpi=144).save(path)


if __name__ == "__main__":
    out = HERE / "assets"
    out.mkdir(exist_ok=True)
    for fid, (title, screen) in FEATURES.items():
        render(scene(title, screen), out / f"feat_{fid}.png")
    print("OK", sorted(p.name for p in out.glob("feat_*.png")))
