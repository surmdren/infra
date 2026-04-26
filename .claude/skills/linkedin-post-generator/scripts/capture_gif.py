#!/usr/bin/env python3
"""
Capture CSS animation frames from an HTML file and export as GIF.

Usage:
    python3 capture_gif.py --html /path/to/visual.html --output /path/to/output.gif

Requirements:
    pip install Pillow
    brew install ffmpeg

How it works:
    Uses Chrome headless --virtual-time-budget to snapshot the page at each
    animation time point, then stitches frames into an animated GIF with ffmpeg.

NOTE: Google Fonts won't load in headless file:// mode — fallback fonts are used.
      The layout and colors render correctly.
"""
import argparse
import os
import shutil
import subprocess
from PIL import Image

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Default animation timestamps (ms). Edit to match your animation duration.
DEFAULT_TIMESTAMPS_MS = [
    0, 80, 160, 250, 350, 450, 550, 650,     # title slide in
    720, 820,                                  # bad box slides in
    900, 960,                                  # VS badge pops
    1050, 1150, 1250,                          # good box slides in
    1450, 1600, 1750, 1900,                    # analogy fades up
    2150, 2300, 2450, 2600, 2750, 2900,        # harness + tags pop
    3050, 3200, 3350, 3500,                    # conclusion fades
    3650, 3800, 3950, 4100, 4250,              # rows appear
    4400, 4600, 4800, 5000, 5200, 5500,        # small lines + signature
    6000,                                      # hold final state
]


def capture_frame(file_url: str, ms: int, out_path: str, tmp_path: str) -> bool:
    cmd = [
        CHROME,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--virtual-time-budget={ms}",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={tmp_path}",
        "--window-size=1080,1167",
        "--hide-scrollbars",
        file_url,
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=20)
        if os.path.exists(tmp_path):
            img = Image.open(tmp_path)
            img.crop((0, 0, 1080, 1080)).save(out_path)
            os.remove(tmp_path)
            return True
    except subprocess.TimeoutExpired:
        pass
    return False


def build_gif(frames: list, output_path: str, scale: int = 540):
    """frames: list of (ms, path) tuples"""
    tmp_dir = os.path.dirname(frames[0][1])
    concat_list = os.path.join(tmp_dir, "concat.txt")

    with open(concat_list, "w") as f:
        for i, (ms, path) in enumerate(frames):
            if not os.path.exists(path):
                continue
            duration = (frames[i + 1][0] - ms) / 1000.0 if i + 1 < len(frames) else 2.5
            f.write(f"file '{path}'\n")
            f.write(f"duration {duration:.3f}\n")
        f.write(f"file '{frames[-1][1]}'\n")  # ffmpeg needs last file repeated

    palette_path = os.path.join(tmp_dir, "palette.png")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-vf", f"scale={scale}:-1:flags=lanczos,palettegen=stats_mode=diff",
        palette_path,
    ], capture_output=True)

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-i", palette_path,
        "-lavfi", f"scale={scale}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5",
        output_path,
    ], capture_output=True)


def main():
    parser = argparse.ArgumentParser(description="Capture HTML animation as GIF")
    parser.add_argument("--html", required=True, help="Absolute path to HTML file")
    parser.add_argument("--output", required=True, help="Output GIF path")
    parser.add_argument("--scale", type=int, default=1080, help="Output width in px (default: 1080)")
    args = parser.parse_args()

    html_path = os.path.abspath(args.html)
    file_url = f"file://{html_path}"
    out_dir = "/tmp/gif_frames"
    shutil.rmtree(out_dir, ignore_errors=True)
    os.makedirs(out_dir)

    print(f"HTML: {html_path}")
    print(f"Output: {args.output}")
    print(f"Capturing {len(DEFAULT_TIMESTAMPS_MS)} frames...")

    captured = []
    for i, ms in enumerate(DEFAULT_TIMESTAMPS_MS):
        frame_path = os.path.join(out_dir, f"frame_{i:03d}.png")
        tmp_path = f"/tmp/gif_raw_{i:03d}.png"
        ok = capture_frame(file_url, ms, frame_path, tmp_path)
        status = "✓" if ok else "✗ (skipped)"
        print(f"  [{i+1}/{len(DEFAULT_TIMESTAMPS_MS)}] t={ms}ms {status}")
        if ok:
            captured.append((ms, frame_path))

    print(f"\nBuilding GIF from {len(captured)} frames...")
    build_gif(captured, args.output, scale=args.scale)

    if os.path.exists(args.output):
        size_kb = os.path.getsize(args.output) / 1024
        print(f"\nGIF saved: {args.output} ({size_kb:.0f} KB)")
    else:
        print("\nERROR: GIF not created")


if __name__ == "__main__":
    main()
