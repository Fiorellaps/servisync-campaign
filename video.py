"""Genera campaign/out/servisync_reel_con_voz.mp4 y servisync_reel_sin_audio.mp4: stories con voz en off (macOS `say`), zoom suave y transiciones.

Uso:  .venv/bin/python campaign/build.py && .venv/bin/python campaign/video.py
Requiere: ffmpeg, ffprobe y el comando `say` de macOS (voz española).
"""
import subprocess
import tempfile
from pathlib import Path

OUT = Path(__file__).parent / "out"
VOZ = Path(__file__).parent / "voz"   # grabaciones propias: voz/escena_1.m4a ... escena_5.m4a (mp3, wav, aiff, m4a)
VOICE = "Mónica"
RATE = 175          # palabras por minuto
T = 0.8             # duración de cada transición (s)
FPS = 30
TRANSITIONS = ["smoothleft", "fadewhite", "smoothright", "fadeblack"]  # entre escenas 1-2, 2-3, ...

# "Servi Sinc" se escribe fonético para que la voz lo pronuncie bien.
NARRATION = [
    "Tus partes de trabajo, sin papeles. Rellena, firma y envía en minutos con Servi Sinc.",
    "Sube tu PDF y lo convertimos en un formulario. Detectamos los campos automáticamente.",
    "Haz fotos y recoge la firma del cliente, ahí mismo, sin volver a la oficina.",
    "Cada cambio queda guardado. Nada se pierde, todo se encuentra.",
    "Digitaliza tus partes hoy mismo. Servi Sinc Digital Solutions. Solicita tu demo.",
]


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def duration(path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       check=True, capture_output=True, text=True)
    return float(r.stdout.strip())


def main():
    tmp = Path(tempfile.mkdtemp())
    audios, lens = [], []
    for i, line in enumerate(NARRATION, 1):
        own = next(iter(sorted(VOZ.glob(f"escena_{i}.*"))), None)
        if own:   # tu grabación: se normaliza y se recortan silencios al principio y al final
            a = tmp / f"v{i}.wav"
            run("ffmpeg", "-y", "-loglevel", "error", "-i", own, "-af",
                "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                "silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5",
                "-ar", 44100, "-ac", 1, a)
            print(f"escena {i}: usando {own.name}")
        else:
            a = tmp / f"v{i}.wav"
            run("say", "-v", VOICE, "-r", RATE, "-o", a, "--data-format=LEI16@44100", line)
            print(f"escena {i}: voz sintética (no hay voz/escena_{i}.*)")
        audios.append(a)
        lens.append(duration(a))

    durs = [l + 2 * T for l in lens]                     # escena = entrada + voz + salida
    starts = [0.0]
    for d in durs[:-1]:
        starts.append(starts[-1] + d - T)
    total = starts[-1] + durs[-1]

    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for i in range(5):
        cmd += ["-framerate", FPS, "-loop", "1", "-t", f"{durs[i]:.3f}", "-i", OUT / f"story_{i+1}.png"]
    for a in audios:
        cmd += ["-i", a]

    f = []
    for i in range(5):
        frames = int(durs[i] * FPS) + 1
        # zoom lento (entrada en escenas pares, salida en impares) sobre imagen ampliada 2x para evitar saltos
        z = f"min(1+0.06*on/{frames},1.06)" if i % 2 == 0 else f"max(1.06-0.06*on/{frames},1)"
        f.append(f"[{i}:v]scale=2160:3840,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                 f":d=1:s=1080x1920:fps={FPS},setsar=1[s{i}]")
    prev = "s0"
    for i in range(1, 5):
        off = starts[i]
        f.append(f"[{prev}][s{i}]xfade=transition={TRANSITIONS[i-1]}:duration={T}:offset={off:.3f}[x{i}]")
        prev = f"x{i}"
    f.append(f"[{prev}]fade=t=out:st={total-0.5:.3f}:d=0.5,format=yuv420p[v]")
    for i in range(5):
        ms = int((starts[i] + T) * 1000)
        f.append(f"[{5+i}:a]adelay={ms}|{ms},volume=1.0[a{i}]")
    f.append("".join(f"[a{i}]" for i in range(5)) + "amix=inputs=5:normalize=0,apad,"
             f"atrim=0:{total:.3f},afade=t=out:st={total-0.5:.3f}:d=0.5[a]")

    cmd += ["-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]", "-r", FPS,
            "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
            OUT / "servisync_reel_con_voz.mp4"]
    run(*cmd)
    run("ffmpeg", "-y", "-loglevel", "error", "-i", OUT / "servisync_reel_con_voz.mp4", "-an", "-c:v", "copy",
        "-movflags", "+faststart", OUT / "servisync_reel_sin_audio.mp4")
    print(f"OK servisync_reel_con_voz.mp4 y servisync_reel_sin_audio.mp4 ({total:.1f} s)")


if __name__ == "__main__":
    main()
