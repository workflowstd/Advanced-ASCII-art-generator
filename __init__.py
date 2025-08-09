import bpy
import os
import numpy as np
from PIL import Image, ImageOps, ImageColor
import time

bl_info = {
    "name": "Advanced ASCII Art Generator",
    "author": "workflowstd.tech (xmm0)",
    "version": (1, 2),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Tools",
    "description": "Renders the current view as customizable ASCII art",
    "warning": "",
    "category": "Render",
}

# Character set presets
CHAR_PRESETS = {
    "DETAILED": "@WM#gB8&$QdENbRqpAHkZDPXhKUmFwGVO0eS5a3I4oJLxznu2vcty1jYf7T9srC}{l?i|/()=+*><[]!^~-_;:,\".`' ",
    "MEDIUM": "@%#*+=-:. ",
    "SIMPLE": "@#=-. ",
    "FULL": "".join(chr(i) for i in range(32, 127)),
    "BLOCKS": "█▓▒░ ",
    "INVERTED": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
}

class ASCII_ART_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    ascii_width: bpy.props.IntProperty(
        name="ASCII Width",
        description="Width of ASCII art in characters",
        default=300,
        min=50,
        max=1000
    )
    
    output_dir: bpy.props.StringProperty(
        name="Output Directory",
        description="Directory to save ASCII art",
        subtype='DIR_PATH',
        default=os.path.join(os.path.expanduser("~"), "Desktop", "ASCII_Art")
    )
    
    char_preset: bpy.props.EnumProperty(
        name="Character Preset",
        description="Select a character preset",
        items=[
            ('DETAILED', "Detailed", "Detailed character set"),
            ('MEDIUM', "Medium", "Medium character set"),
            ('SIMPLE', "Simple", "Simple character set"),
            ('FULL', "Full ASCII", "All keyboard characters"),
            ('BLOCKS', "Blocks", "Block characters only"),
            ('INVERTED', "Inverted", "Inverted density characters"),
            ('CUSTOM', "Custom", "Use custom characters")
        ],
        default='DETAILED'
    )
    
    custom_chars: bpy.props.StringProperty(
        name="Custom Characters",
        description="Enter custom characters for ASCII art",
        default=" .:-=+*#%@"
    )
    
    bg_color: bpy.props.FloatVectorProperty(
        name="Background Color",
        description="Background color for PNG output",
        subtype='COLOR',
        size=3,
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0
    )
    
    text_color: bpy.props.FloatVectorProperty(
        name="Text Color",
        description="Text color for ASCII characters",
        subtype='COLOR',
        size=3,
        default=(0.0, 0.0, 0.0),
        min=0.0,
        max=1.0
    )
    
    invert_brightness: bpy.props.BoolProperty(
        name="Invert Brightness",
        description="Invert brightness mapping (darker = more dense)",
        default=False
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "ascii_width")
        layout.prop(self, "output_dir")
        
        # Character set selection
        row = layout.row()
        row.prop(self, "char_preset", text="Preset")
        
        if self.char_preset == 'CUSTOM':
            layout.prop(self, "custom_chars")
        
        # Colors
        layout.label(text="PNG Colors:")
        row = layout.row()
        row.prop(self, "bg_color", text="BG")
        row.prop(self, "text_color", text="Text")
        
        layout.prop(self, "invert_brightness")

class RENDER_OT_ascii_art(bpy.types.Operator):
    bl_idname = "render.ascii_art"
    bl_label = "Render ASCII Art"
    bl_description = "Render current view as ASCII art"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        ASCII_WIDTH = prefs.ascii_width
        output_dir = prefs.output_dir
        
        # Get selected character set
        if prefs.char_preset == 'CUSTOM':
            ascii_chars = prefs.custom_chars
        else:
            ascii_chars = CHAR_PRESETS[prefs.char_preset]
            
        if not ascii_chars:
            self.report({'ERROR'}, "Character set is empty!")
            return {'CANCELLED'}
        
        # Convert colors from [0-1] to [0-255]
        bg_color = tuple(int(c * 255) for c in prefs.bg_color)
        text_color = tuple(int(c * 255) for c in prefs.text_color)

        original_engine = None
        try:
            print("=== Starting ASCII art creation ===")
            start_time = time.time()
            
            # Configure Eevee rendering
            original_engine = self.setup_eevee_rendering(context)
            
            # Camera check
            if not context.scene.camera:
                self.report({'ERROR'}, "Camera not set!")
                return {'CANCELLED'}
            
            # Create temp directory
            os.makedirs(output_dir, exist_ok=True)
            temp_path = os.path.join(output_dir, "temp_render.png")
            
            # Render current camera view
            print("Rendering current camera view...")
            if not self.render_current_view(context, temp_path):
                self.report({'ERROR'}, "Render failed!")
                return {'CANCELLED'}
            
            # Verify render result
            if not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                self.report({'ERROR'}, f"Render failed: {temp_path}")
                return {'CANCELLED'}
            
            # Load image
            img = Image.open(temp_path)
            
            # Enhance contrast
            img = self.enhance_contrast(img)
            
            # Convert to ASCII
            ascii_art = self.convert_to_ascii(img, ASCII_WIDTH, ascii_chars, prefs.invert_brightness)
            
            if not ascii_art:
                self.report({'ERROR'}, "Failed to create ASCII art")
                return {'CANCELLED'}
            
            # Save results
            text_path, image_path = self.save_ascii_art(ascii_art, output_dir, bg_color, text_color)
            
            # Delete temp file
            try:
                os.remove(temp_path)
                print("Temporary render file deleted")
            except:
                pass
            
            elapsed_time = time.time() - start_time
            print("=" * 50)
            print(f"SUCCESS! ASCII art created in {elapsed_time:.1f} seconds")
            print(f"Text file: {text_path}")
            print(f"Image: {image_path}")
            print("=" * 50)
            
            self.report({'INFO'}, f"ASCII art created in {elapsed_time:.1f}s")
            return {'FINISHED'}
            
        except Exception as e:
            print("=" * 50)
            print(f"CRITICAL ERROR: {str(e)}")
            print("=" * 50)
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}
        finally:
            # Always restore render settings
            if original_engine:
                self.restore_render_settings(context, original_engine)

    def setup_eevee_rendering(self, context):
        """Configure fast Eevee rendering"""
        try:
            # Save current render engine
            original_engine = context.scene.render.engine
            
            # Switch to Eevee
            context.scene.render.engine = 'BLENDER_EEVEE'
            print("Eevee rendering activated")
            
            # Optimized settings
            context.scene.eevee.taa_render_samples = 48
            context.scene.eevee.use_gtao = True
            context.scene.eevee.use_bloom = False
            context.scene.eevee.use_ssr = False
            context.scene.eevee.use_volumetric = False
            
            return original_engine
        except Exception as e:
            print(f"Eevee setup error: {str(e)}")
            return None

    def restore_render_settings(self, context, original_engine):
        """Restore original render settings"""
        if original_engine:
            try:
                context.scene.render.engine = original_engine
                print("Original render settings restored")
            except:
                print("Error restoring render settings")

    def enhance_contrast(self, img):
        """Enhance contrast while preserving details"""
        try:
            # Convert to grayscale with extended palette
            img = img.convert('L')
            
            # Auto contrast with detail protection
            img = ImageOps.autocontrast(img, cutoff=1, ignore=1)
            
            return img
        except Exception as e:
            print(f"Contrast enhancement error: {str(e)}")
            return img

    def convert_to_ascii(self, img, ASCII_WIDTH, ascii_chars, invert_brightness):
        """Convert image to ASCII art"""
        try:
            # Calculate proportions
            aspect_ratio = img.height / img.width
            new_height = int(ASCII_WIDTH * aspect_ratio * 0.55)
            new_height = max(1, new_height)
            
            # Resize image
            img = img.resize((ASCII_WIDTH, new_height))
            print(f"ASCII dimensions: {ASCII_WIDTH}x{new_height} characters")
            print(f"Using character set with {len(ascii_chars)} characters")
            
            # Convert to array
            pixels = np.array(img)
            ascii_art = []
            
            # Calculate brightness step for characters
            char_step = 256 / len(ascii_chars)
            
            # Invert brightness if needed
            if invert_brightness:
                pixels = 255 - pixels
            
            for row in pixels:
                line = ""
                for p in row:
                    # Calculate character index
                    char_index = min(int(p / char_step), len(ascii_chars) - 1)
                    line += ascii_chars[char_index]
                ascii_art.append(line)
            
            return "\n".join(ascii_art)
        except Exception as e:
            print(f"ASCII conversion error: {str(e)}")
            return ""

    def save_ascii_art(self, ascii_art, output_dir, bg_color, text_color):
        """Save ASCII art to files"""
        try:
            # Save to text file
            text_path = os.path.join(output_dir, "ascii_art.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(ascii_art)
            print(f"Text file saved: {text_path}")
            
            # Create image from ASCII
            char_width = 6
            char_height = 12
            
            # Calculate image dimensions
            lines = ascii_art.split('\n')
            img_width = len(lines[0]) * char_width if lines else ASCII_WIDTH * char_width
            img_height = len(lines) * char_height
            
            # Create new image with background color
            from PIL import ImageDraw, ImageFont
            img = Image.new('RGB', (img_width, img_height), color=bg_color)
            d = ImageDraw.Draw(img)
            
            # Load monospace font
            font = None
            try:
                # Try different fonts
                for font_name in ["cour.ttf", "consola.ttf", "DejaVuSansMono.ttf", "LiberationMono-Regular.ttf"]:
                    try:
                        font = ImageFont.truetype(font_name, 10)
                        break
                    except:
                        continue
            except:
                pass
            
            # Draw text with specified color
            y = 0
            for line in lines:
                d.text((0, y), line, fill=text_color, font=font)
                y += char_height
            
            # Save image
            image_path = os.path.join(output_dir, "ascii_art.png")
            img.save(image_path)
            print(f"ASCII image saved: {image_path}")
            
            return text_path, image_path
        except Exception as e:
            print(f"ASCII save error: {str(e)}")
            return None, None

    def render_current_view(self, context, output_path):
        """Render current camera view"""
        try:
            # Save current settings
            original_filepath = context.scene.render.filepath
            original_file_format = context.scene.render.image_settings.file_format
            
            # Set temporary settings
            context.scene.render.filepath = output_path
            context.scene.render.image_settings.file_format = 'PNG'
            context.scene.render.image_settings.color_mode = 'RGB'
            context.scene.render.resolution_percentage = 100  # Full resolution
            
            # Execute render
            bpy.ops.render.render(write_still=True)
            
            # Restore settings
            context.scene.render.filepath = original_filepath
            context.scene.render.image_settings.file_format = original_file_format
            
            return True
        except Exception as e:
            print(f"Render error: {str(e)}")
            return False

class VIEW3D_PT_ascii_art(bpy.types.Panel):
    bl_label = "ASCII Art Render"
    bl_idname = "VIEW3D_PT_ascii_art"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ASCII art'
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        prefs = context.preferences.addons[__name__].preferences
        
        # Main settings
        col = layout.column(align=True)
        col.prop(prefs, "ascii_width")
        col.prop(prefs, "output_dir")
        
        # Character set
        box = layout.box()
        box.label(text="Character Set")
        box.prop(prefs, "char_preset", text="Preset")
        
        if prefs.char_preset == 'CUSTOM':
            box.prop(prefs, "custom_chars")
            
        # Colors
        box = layout.box()
        box.label(text="PNG Colors")
        row = box.row()
        row.prop(prefs, "bg_color", text="Background")
        row = box.row()
        row.prop(prefs, "text_color", text="Text")
        
        # Advanced settings
        box = layout.box()
        box.label(text="Advanced")
        box.prop(prefs, "invert_brightness")
        
        # Render button
        layout.operator("render.ascii_art", icon='RENDER_STILL', text="Render ASCII Art")
        
        # Add uninstall button
        layout.separator()
        layout.operator("preferences.addon_remove", text="Uninstall Add-on", icon='TRASH').module = __name__

def register():
    # Dependency check
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        print("Required libraries not found. Please install Pillow and numpy.")
        return
    
    bpy.utils.register_class(ASCII_ART_Preferences)
    bpy.utils.register_class(RENDER_OT_ascii_art)
    bpy.utils.register_class(VIEW3D_PT_ascii_art)

def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_ascii_art)
    bpy.utils.unregister_class(RENDER_OT_ascii_art)
    bpy.utils.unregister_class(ASCII_ART_Preferences)

if __name__ == "__main__":
    register()