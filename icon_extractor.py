import win32ui
import win32gui
import win32con
import win32api
from PIL import Image
import os

def extract_icon(exe_path, output_path):
    """
    Extracts the large icon from a Windows executable and saves it as a PNG.
    """
    try:
        # Get the large icon handle
        large, small = win32gui.ExtractIconEx(exe_path, 0)
        
        if not large:
            print(f"No icon found for {exe_path}")
            return None

        hIcon = large[0]
        
        # Create a PyCBitmap from the icon
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, 32, 32)
        hdc = hdc.CreateCompatibleDC()
        hdc.SelectObject(hbmp)
        
        # Draw the icon
        hdc.DrawIcon((0, 0), hIcon)
        
        # Convert to PIL Image
        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGBA',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRA', 0, 1
        )
        
        # Save
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
            
        img.save(output_path)
        
        # Cleanup
        win32gui.DestroyIcon(hIcon)
        win32gui.DestroyIcon(small[0]) if small else None
        
        return output_path
        
    except Exception as e:
        print(f"Error extracting icon: {e}")
        return None
