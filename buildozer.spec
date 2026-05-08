# buildozer.spec

[app]

title = pyDarts
package.name = pydarts
package.domain = org.saros

version = 0.1.0

# --- SOURCE ---
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt,pdf,ini

# --- REQUIREMENTS ---
requirements = python3,kivy,kivymd,pillow,pyjnius,fpdf2,https://github.com/fonttools/fonttools/archive/refs/heads/main.zip

# --- UI ---
orientation = portrait
fullscreen = 0

# --- ANDROID ---
android.api = 31
android.minapi = 21
android.target = 31

android.permissions = INTERNET

# --- ARCH ---
android.archs = arm64-v8a

android.add_resources = res

# --- BOOTSTRAP ---
p4a.bootstrap = sdl2

# --- DEBUG ---
log_level = 2

android.allow_backup = False