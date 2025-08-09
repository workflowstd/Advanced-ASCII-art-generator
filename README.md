# Advanced ASCII Art Generator for Blender 4.5.x

## Overview
Blender addon for converting Eevee renders to ASCII art. Requires **Pillow** library for image processing. 

[DOWNLOAD ADDON](https://github.com/workflowstd/Advanced-ASCII-art-generator/releases/download/Release/advanced_ascii_art_generator.zip)

## Preview
### Before
<img width="600" height="600" alt="Untitled" src="https://github.com/user-attachments/assets/9a5858ba-d050-418d-b66b-95e2aa4a8268" />

### After
<img width="600" height="600" alt="ascii_art" src="https://github.com/user-attachments/assets/55c22018-fcfa-4568-b7aa-1da59da7428e" />

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

## `ModuleNotFoundError: No module named 'PIL'` solution
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




