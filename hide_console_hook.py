import subprocess
import sys

# Monkey-patch subprocess.Popen on Windows to always hide the console window
if sys.platform == 'win32':
    _original_popen = subprocess.Popen

    def _patched_popen(*args, **kwargs):
        # Add the CREATE_NO_WINDOW flag
        if 'creationflags' not in kwargs:
            kwargs['creationflags'] = 0x08000000
        
        # Redirect stdin to DEVNULL to prevent it from asking for a console
        if 'stdin' not in kwargs:
            kwargs['stdin'] = subprocess.DEVNULL
            
        # Add STARTUPINFO with SW_HIDE to be absolutely sure
        if 'startupinfo' not in kwargs:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = startupinfo
            
        return _original_popen(*args, **kwargs)

    subprocess.Popen = _patched_popen
