import os, time, psutil, pyautogui, subprocess, screen_brightness_control as sbc
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


def _safe_set_brightness(step: int | None = None, absolute: int | None = None):
    """
    Try WMI -> DDC/CI -> Hotkey simulation
    Returns (True/False, method/error)
    """
    last_err = None

    # --- 1) WMI ---
    try:
        if absolute is not None:
            sbc.set_brightness(int(absolute), method='wmi')
        elif step is not None:
            sbc.set_brightness(f"{'+' if step >= 0 else ''}{step}", method='wmi')
        return True, "wmi"
    except Exception as e:
        last_err = e

    # --- 2) DDC/CI ---
    try:
        if absolute is not None:
            sbc.set_brightness(int(absolute), method='ddc')
        elif step is not None:
            sbc.set_brightness(f"{'+' if step >= 0 else ''}{step}", method='ddc')
        return True, "ddc"
    except Exception as e:
        last_err = e

    # --- 3) Hotkey fallback ---
    try:
        if step is not None:
            presses = max(1, abs(step) // 5)  # 1 press ≈ 5–10%
            key = 'brightnessup' if step > 0 else 'brightnessdown'
            for _ in range(presses):
                pyautogui.press(key)
                time.sleep(0.08)
            return True, "hotkey"
    except Exception as e:
        last_err = e

    return False, last_err


class SystemControl:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))

    # -------- Volume --------
    def volume_up(self):
        current = self.volume.GetMasterVolumeLevelScalar()
        self.volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)

    def volume_down(self):
        current = self.volume.GetMasterVolumeLevelScalar()
        self.volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)


    def mute(self):
        self.volume.SetMute(1, None)

    def unmute(self):
        self.volume.SetMute(0, None)

    # -------- Brightness --------
    def brightness_up(self):
        ok, used = _safe_set_brightness(step=+10)
        if not ok:
            raise RuntimeError(f"Brightness failed: {used}")

    def brightness_down(self):
        ok, used = _safe_set_brightness(step=-10)
        if not ok:
            raise RuntimeError(f"Brightness failed: {used}")

    def brightness_set(self, value: int):
        value = max(0, min(100, int(value)))
        ok, used = _safe_set_brightness(absolute=value)
        if not ok:
            raise RuntimeError(f"Brightness failed: {used}")

    # -------- System Power --------
    def lock(self):
        os.system("rundll32.exe user32.dll,LockWorkStation")

    def shutdown(self):
        os.system("shutdown /s /t 1")

    def restart(self):
        os.system("shutdown /r /t 1")

    def sleep(self):
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
