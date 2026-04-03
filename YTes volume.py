from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# Check if the system volume can be accessed
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

# Get the current volume level as a float (0.0 to 1.0)
current_volume = volume.GetMasterVolumeLevelScalar()
print(f"Current system volume: {current_volume * 100}%")
