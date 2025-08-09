# Advanced ASCII Art Generator for Blender 4.5.x

## Overview
Blender addon for converting Eevee renders to ASCII art. Requires **Pillow** library for image processing. 

## Key Features
- Converts rendered images to ASCII art
- Automatic grayscale conversion and resizing
- Pixel brightness analysis for character mapping

## Pillow Dependency
**Required for:**
1. Loading/saving rendered images
2. Converting images to grayscale
3. Resizing images for ASCII conversion
4. Pixel brightness analysis
5. Character mapping by luminance values

**Without Pillow:**  
`ModuleNotFoundError: No module named 'PIL'` will occur

## Installation Script
```python
import bpy
import subprocess
import sys
import numpy as np

try:
    from PIL import Image, ImageOps
    print("Pillow is already installed!")
except ImportError:
    python_exe = sys.executable
    subprocess.call([python_exe, "-m", "pip", "install", "Pillow"])
    print("Pillow installed. RESTART BLENDER")
```

Thanks for installing advanced ascii art generator 

by workflow std
(xmm0 - telegram https://t.me/telllmewhatt)




