from jnius import autoclass, cast
from android.runnable import run_on_ui_thread
from kivy.utils import platform

# Tyto třídy definujeme hned, protože víme, že jedeme na Androidu
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
String = autoclass('java.lang.String')
File = autoclass('java.io.File')
FileProvider = autoclass('androidx.core.content.FileProvider')

@run_on_ui_thread
def share_pdf(filepath, title="Otevřít PDF"):
    try:
        activity = PythonActivity.mActivity
        pdf_file = File(filepath)

        # Dynamické authority: cz.vasedomena.darts.fileprovider
        authority = activity.getPackageName() + ".fileprovider"

        # Vytvoření bezpečného content:// URI přes FileProvider
        uri = FileProvider.getUriForFile(
            activity,
            String(authority),
            pdf_file
        )

        intent = Intent(Intent.ACTION_VIEW)
        intent.setDataAndType(
            cast('android.net.Uri', uri),
            "application/pdf"
        )

        # Klíčová oprávnění a flagy pro Android
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        intent.addFlags(Intent.FLAG_ACTIVITY_NO_HISTORY)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)

        # Vytvoření a spuštění dialogu "Otevřít pomocí"
        chooser = Intent.createChooser(intent, cast('java.lang.CharSequence', String(title)))
        chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        
        activity.startActivity(chooser)
        
    except Exception as e:
        print(f"Chyba při otevírání PDF: {e}")
