[app]

title = pyDarts
package.name = pydarts
package.domain = org.saros

version = 0.1.0

# --- SOURCE ---
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt,pdf

# --- REQUIREMENTS ---
requirements = python3,kivy,kivymd,pillow,pyjnius,fpdf2,fonttools,defusedxml

# --- UI ---
# portrait or landscape
orientation = portrait
fullscreen = 0

# --- ANDROID SDK ---
android.api = 33
android.minapi = 21
android.target = 33

# --- ANDROID PERMISSION ---
android.permissions = INTERNET

# --- ARCH ---
#android.archs = arm64-v8a,armeabi-v7a
android.archs = arm64-v8a

android.add_resources = res
#android.manifest.application_dest = manifest_fragment.xml

#android.enable_androidx = True
#android.gradle_dependencies = androidx.core:core:1.8.0


# --- BOOTSTRAP ---
p4a.bootstrap = sdl2

# --- DEBUG ---
log_level = 2

android.allow_backup = False