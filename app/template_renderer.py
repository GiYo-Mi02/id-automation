"""
Template Rendering Engine
=========================
WYSIWYG-compatible rendering engine for ID card templates.
Supports layer-based templates with text, image, shape, and QR code layers.
"""

import json
import logging
import textwrap
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import qrcode

logger = logging.getLogger(__name__)


# =============================================================================
# FONT MANAGEMENT
# =============================================================================

class FontManager:
    """Manages font loading with fallbacks."""
    
    _cache: Dict[Tuple[str, int, str], ImageFont.FreeTypeFont] = {}
    
    # Common font paths for Windows
    FONT_PATHS = [
        "C:/Windows/Fonts",
        "C:/WINDOWS/FONTS",
        "./fonts",
        "../fonts",
    ]
    
    # Font name to file mapping
    FONT_MAP = {
        'arial': 'arial.ttf',
        'arial bold': 'arialbd.ttf',
        'times new roman': 'times.ttf',
        'times new roman bold': 'timesbd.ttf',
        'calibri': 'calibri.ttf',
        'calibri bold': 'calibrib.ttf',
        'verdana': 'verdana.ttf',
        'verdana bold': 'verdanab.ttf',
        'tahoma': 'tahoma.ttf',
        'tahoma bold': 'tahomabd.ttf',
        'georgia': 'georgia.ttf',
        'georgia bold': 'georgiab.ttf',
        'roboto': 'Roboto-Regular.ttf',
        'roboto bold': 'Roboto-Bold.ttf',
    }
    
    @classmethod
    def get_font(cls, family: str, size: int, weight: str = 'normal') -> ImageFont.FreeTypeFont:
        """Get a font with caching and fallbacks."""
        cache_key = (family.lower(), size, weight)
        
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        font = cls._load_font(family, size, weight)
        cls._cache[cache_key] = font
        return font
    
    @classmethod
    def _load_font(cls, family: str, size: int, weight: str) -> ImageFont.FreeTypeFont:
        """Load a font file."""
        family_lower = family.lower()
        is_bold = weight in ('bold', '600', '700', '800', '900')
        
        # Build font key
        font_key = f"{family_lower} bold" if is_bold else family_lower
        
        # Try to find the font file
        font_file = cls.FONT_MAP.get(font_key, cls.FONT_MAP.get(family_lower))
        
        if font_file:
            for base_path in cls.FONT_PATHS:
                font_path = Path(base_path) / font_file
                if font_path.exists():
                    try:
                        return ImageFont.truetype(str(font_path), size)
                    except Exception as e:
                        logger.warning(f"Failed to load font {font_path}: {e}")
        
        # Fallback to system fonts
        try:
            if is_bold:
                return ImageFont.truetype("arialbd.ttf", size)
            return ImageFont.truetype("arial.ttf", size)
        except:
            pass
        
        # Ultimate fallback
        logger.warning(f"Using default font for {family} {size} {weight}")
        return ImageFont.load_default()


# =============================================================================
# LAYER RENDERERS
# =============================================================================

def render_text_layer(
    card: Image.Image,
    layer: Dict[str, Any],
    data: Dict[str, Any],
    canvas_width: int,
) -> Image.Image:
    """Render a text layer with support for rotation."""
    # Get text content
    field = layer.get('field', '')
    if field == 'static':
        text = layer.get('text', '')
        logger.debug(f"   Static text layer: '{text}'")
    else:
        # Dynamic field - look up value from data
        text = str(data.get(field, layer.get('text', '')))
        logger.debug(f"   Dynamic field '{field}' → '{text}' (fallback: '{layer.get('text', '')}')")
    
    if not text:
        logger.warning(f"   Skipping empty text layer (field: {field})")
        return card
    
    # Apply text transformations
    if layer.get('uppercase'):
        text = text.upper()
    elif layer.get('lowercase'):
        text = text.lower()
    
    # Get font
    font_family = layer.get('fontFamily', 'Arial')
    font_size = int(layer.get('fontSize', 16))
    font_weight = layer.get('fontWeight', 'normal')
    font = FontManager.get_font(font_family, font_size, font_weight)
    
    # Get position and dimensions
    x = layer.get('x', 0)
    y = layer.get('y', 0)
    width = layer.get('width', 200)
    height = layer.get('height', 50)
    text_align = layer.get('textAlign', 'left')
    word_wrap = layer.get('wordWrap', False)
    line_height = layer.get('lineHeight', 1.2)
    color = layer.get('color', '#000000')
    rotation = layer.get('rotation', 0)
    
    # Handle word wrap
    if word_wrap and width > 0:
        # Calculate approximate characters per line
        avg_char_width = font_size * 0.6  # Approximation
        chars_per_line = max(1, int(width / avg_char_width))
        lines = textwrap.wrap(text, width=chars_per_line)
    else:
        lines = [text]
    
    # Calculate line spacing
    line_spacing = int(font_size * line_height)
    
    # Calculate total text block dimensions
    total_text_height = len(lines) * line_spacing
    max_text_width = 0
    for line in lines:
        bbox = font.getbbox(line)
        line_width = bbox[2] - bbox[0]
        max_text_width = max(max_text_width, line_width)
    
    # If rotation is needed, create a temporary image for the text
    if rotation != 0:
        # Create a temporary transparent image large enough for the text
        # Use padding to ensure text isn't clipped during rotation
        padding = 20
        temp_width = max(width, max_text_width) + padding * 2
        temp_height = max(height, total_text_height) + padding * 2
        temp_img = Image.new('RGBA', (temp_width, temp_height), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        
        # Draw text on temporary image
        for i, line in enumerate(lines):
            line_y = padding + (i * line_spacing)
            
            # Calculate x position based on alignment
            if text_align == 'center':
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                line_x = padding + (max_text_width - text_width) // 2
            elif text_align == 'right':
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                line_x = padding + max_text_width - text_width
            else:  # left or justify
                line_x = padding
            
            # Draw text shadow if configured
            shadow = layer.get('textShadow')
            if shadow:
                shadow_x = line_x + shadow.get('offsetX', 0)
                shadow_y = line_y + shadow.get('offsetY', 1)
                shadow_color = shadow.get('color', 'rgba(0,0,0,0.25)')
                temp_draw.text((shadow_x, shadow_y), line, fill=shadow_color, font=font)
            
            # Draw main text
            temp_draw.text((line_x, line_y), line, fill=color, font=font)
        
        # Rotate the temporary image
        # Use expand=True to prevent clipping
        rotated_img = temp_img.rotate(-rotation, expand=True, resample=Image.Resampling.BICUBIC)
        
        # Calculate paste position
        # The rotation changes the image dimensions, so we need to adjust
        rotated_width, rotated_height = rotated_img.size
        
        # Calculate offset to keep text centered on original anchor point
        # This maintains the visual position relative to the layer's x, y coordinates
        paste_x = x - (rotated_width - temp_width) // 2
        paste_y = y - (rotated_height - temp_height) // 2
        
        # Paste the rotated text onto the main card
        card.paste(rotated_img, (paste_x, paste_y), rotated_img)
        
    else:
        # No rotation - draw directly on the card
        draw = ImageDraw.Draw(card)
        
        for i, line in enumerate(lines):
            line_y = y + (i * line_spacing)
            
            # Calculate x position based on alignment
            if text_align == 'center':
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                line_x = x + (width - text_width) // 2
            elif text_align == 'right':
                bbox = font.getbbox(line)
                text_width = bbox[2] - bbox[0]
                line_x = x + width - text_width
            else:  # left or justify
                line_x = x
            
            # Draw text shadow if configured
            shadow = layer.get('textShadow')
            if shadow:
                shadow_x = line_x + shadow.get('offsetX', 0)
                shadow_y = line_y + shadow.get('offsetY', 1)
                shadow_color = shadow.get('color', 'rgba(0,0,0,0.25)')
                draw.text((shadow_x, shadow_y), line, fill=shadow_color, font=font)
            
            # Draw main text
            draw.text((line_x, line_y), line, fill=color, font=font)
    
    return card


def render_image_layer(
    card: Image.Image,
    layer: Dict[str, Any],
    data: Dict[str, Any],
    photo_image: Optional[Image.Image] = None,
    base_path: str = '',
) -> Image.Image:
    """Render an image layer."""
    x = int(layer.get('x', 0))
    y = int(layer.get('y', 0))
    width = int(layer.get('width', 200))
    height = int(layer.get('height', 200))
    
    # Get image source
    field = layer.get('field')
    src = layer.get('src')
    
    img = None
    
    if field == 'photo' and photo_image:
        img = photo_image.copy()
    elif src:
        # Handle URL sources from uploaded images
        img_path = src
        
        # Convert URL to local file path for uploaded images
        if 'http' in src and 'uploads' in src:
            # Extract the filename from URL: http://localhost:8000/uploads/file.png -> file.png
            if '/uploads/' in src:
                filename = src.split('/uploads/')[-1]
                img_path = Path('data/uploads') / filename
                logger.debug(f"Converted URL to path: {src} -> {img_path}")
            elif '/static/uploads/' in src:
                filename = src.split('/static/uploads/')[-1]
                img_path = Path('data/uploads') / filename
                logger.debug(f"Converted URL to path: {src} -> {img_path}")
        else:
            # Handle relative or absolute paths
            img_path = Path(base_path) / src if base_path and not Path(src).is_absolute() else Path(src)
        
        # Load the image
        if Path(img_path).exists():
            try:
                img = Image.open(img_path).convert('RGBA')
                logger.debug(f"Loaded image: {img_path} ({img.size})")
            except Exception as e:
                logger.warning(f"Failed to load image {img_path}: {e}")
        else:
            logger.warning(f"Image not found: {img_path}")
    
    if not img:
        return card
    
    # Apply object fit
    object_fit = layer.get('objectFit', 'cover')
    
    if object_fit == 'cover':
        img = ImageOps.fit(img, (width, height), centering=(0.5, 0.5))
    elif object_fit == 'contain':
        img.thumbnail((width, height), Image.Resampling.LANCZOS)
        # Center the image on transparent background
        new_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        paste_x = (width - img.width) // 2
        paste_y = (height - img.height) // 2
        new_img.paste(img, (paste_x, paste_y), mask=img)  # Preserve transparency
        img = new_img
    elif object_fit == 'fill':
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    # 'none' keeps original size
    
    # Apply border radius
    border_radius = layer.get('borderRadius', 0)
    if border_radius > 0:
        img = apply_rounded_corners(img, border_radius)
    
    # Paste onto card
    if img.mode == 'RGBA':
        card.paste(img, (x, y), mask=img)
    else:
        card.paste(img, (x, y))
    
    # Draw border if configured
    border = layer.get('border')
    if border:
        draw = ImageDraw.Draw(card)
        border_width = border.get('width', 1)
        border_color = border.get('color', '#000000')
        draw.rectangle(
            [x, y, x + width, y + height],
            outline=border_color,
            width=border_width
        )
    
    return card


def apply_rounded_corners(img: Image.Image, radius: int) -> Image.Image:
    """Apply rounded corners to an image."""
    # Create a mask with rounded corners
    mask = Image.new('L', img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
    
    # Apply mask
    result = Image.new('RGBA', img.size, (0, 0, 0, 0))
    result.paste(img, (0, 0))
    result.putalpha(mask)
    
    return result


def render_shape_layer(
    draw: ImageDraw.ImageDraw,
    layer: Dict[str, Any],
) -> None:
    """Render a shape layer."""
    x = layer.get('x', 0)
    y = layer.get('y', 0)
    width = layer.get('width', 100)
    height = layer.get('height', 100)
    shape = layer.get('shape', 'rectangle')
    fill = layer.get('fill')
    stroke = layer.get('stroke')
    stroke_width = layer.get('strokeWidth', 1)
    border_radius = layer.get('borderRadius', 0)
    
    if shape == 'rectangle':
        if border_radius > 0:
            draw.rounded_rectangle(
                [x, y, x + width, y + height],
                radius=border_radius,
                fill=fill,
                outline=stroke,
                width=stroke_width if stroke else 0
            )
        else:
            draw.rectangle(
                [x, y, x + width, y + height],
                fill=fill,
                outline=stroke,
                width=stroke_width if stroke else 0
            )
    elif shape == 'circle':
        draw.ellipse(
            [x, y, x + width, y + height],
            fill=fill,
            outline=stroke,
            width=stroke_width if stroke else 0
        )
    elif shape == 'line':
        draw.line(
            [x, y, x + width, y + height],
            fill=stroke or fill,
            width=stroke_width
        )


def render_qr_code_layer(
    card: Image.Image,
    layer: Dict[str, Any],
    data: Dict[str, Any],
) -> Image.Image:
    """Render a QR code layer."""
    x = int(layer.get('x', 0))
    y = int(layer.get('y', 0))
    width = int(layer.get('width', 100))
    height = int(layer.get('height', 100))
    
    field = layer.get('field', 'id_number')
    content = str(data.get(field, ''))
    
    if not content:
        return card
    
    fg_color = layer.get('foregroundColor', '#000000')
    bg_color = layer.get('backgroundColor', '#ffffff')
    error_level = layer.get('errorCorrectionLevel', 'M')
    
    # Map error level
    error_map = {
        'L': qrcode.constants.ERROR_CORRECT_L,
        'M': qrcode.constants.ERROR_CORRECT_M,
        'Q': qrcode.constants.ERROR_CORRECT_Q,
        'H': qrcode.constants.ERROR_CORRECT_H,
    }
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_map.get(error_level, qrcode.constants.ERROR_CORRECT_M),
        box_size=10,
        border=1,
    )
    qr.add_data(content)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color=fg_color, back_color=bg_color)
    qr_img = qr_img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Convert to RGBA if needed
    if qr_img.mode != 'RGBA':
        qr_img = qr_img.convert('RGBA')
    
    card.paste(qr_img, (x, y))
    return card


# =============================================================================
# MAIN RENDERER
# =============================================================================

class TemplateRenderer:
    """
    Renders ID cards from layer-based templates.
    Ensures WYSIWYG output matching the editor preview.
    """
    
    def __init__(self, template_folder: str = 'data/templates'):
        self.template_folder = Path(template_folder)
    
    def render(
        self,
        template: Dict[str, Any],
        data: Dict[str, Any],
        photo_image: Optional[Image.Image] = None,
        side: str = 'front',
    ) -> Image.Image:
        """
        Render a single side of an ID card.
        
        Args:
            template: Template configuration with canvas and layers
            data: Student/teacher data dictionary
            photo_image: Pre-processed photo image (optional)
            side: 'front' or 'back'
        
        Returns:
            Rendered PIL Image
        """
        # Get canvas config
        canvas = template.get('canvas', {})
        width = canvas.get('width', 591)
        height = canvas.get('height', 1004)
        bg_color = canvas.get('backgroundColor', '#FFFFFF')
        
        # Create base card
        card = Image.new('RGBA', (width, height), bg_color)
        
        # Get side-specific data (includes backgroundImage and layers)
        side_data = template.get(side, {})
        bg_image = side_data.get('backgroundImage')
        
        # Load background image if specified
        if bg_image:
            bg_path = None
            
            # Parse URL to filesystem path
            if bg_image.startswith('/api/templates/backgrounds/'):
                # API URL format: /api/templates/backgrounds/teacher/file.png
                # Extract: teacher/file.png and prepend data/templates/
                parts = bg_image.split('/api/templates/backgrounds/', 1)
                if len(parts) == 2:
                    relative_path = parts[1]  # e.g., "teacher/file.png"
                    bg_path = Path('data') / 'templates' / relative_path
                    logger.debug(f"Resolved API URL {bg_image} → {bg_path}")
            elif bg_image.startswith('/'):
                # Legacy absolute path - extract only filename (no subdirs)
                bg_path = Path('data') / 'templates' / Path(bg_image).name
            else:
                # Relative path - use as-is
                bg_path = self.template_folder / bg_image
            
            if bg_path and bg_path.exists():
                try:
                    logger.info(f"Loading background: {bg_path}")
                    bg = Image.open(bg_path).convert('RGBA')
                    bg = bg.resize((width, height), Image.Resampling.LANCZOS)
                    card.paste(bg, (0, 0))
                except Exception as e:
                    logger.error(f"FAILED to load background {bg_path}: {e}")
            else:
                logger.error(f"CRITICAL: Background file NOT FOUND at {bg_path}. Template will render WHITE.")
        
        # Get layers for the specified side
        layers = side_data.get('layers', [])
        logger.info(f"Rendering {side} side with {len(layers)} layers")
        
        if not layers:
            logger.warning(f"NO LAYERS found for {side} side! Template will be blank except background.")
        
        # Sort layers by zIndex
        sorted_layers = sorted(layers, key=lambda l: l.get('zIndex', 0))
        
        # Create draw context
        draw = ImageDraw.Draw(card)
        
        # Render each layer
        for layer in sorted_layers:
            if not layer.get('visible', True):
                continue
            
            layer_type = layer.get('type')
            opacity = layer.get('opacity', 1.0)
            
            try:
                if layer_type == 'text':
                    logger.debug(f"Rendering text layer: {layer.get('id')} - {layer.get('field')}")
                    card = render_text_layer(card, layer, data, width)
                    draw = ImageDraw.Draw(card)  # Recreate draw after text rendering
                elif layer_type == 'image':
                    logger.debug(f"Rendering image layer: {layer.get('id')}")
                    card = render_image_layer(
                        card, layer, data, photo_image,
                        str(self.template_folder)
                    )
                    draw = ImageDraw.Draw(card)  # Recreate draw after image paste
                elif layer_type == 'shape':
                    logger.debug(f"Rendering shape layer: {layer.get('id')}")
                    render_shape_layer(draw, layer)
                elif layer_type == 'qr_code':
                    logger.debug(f"Rendering QR code layer: {layer.get('id')}")
                    card = render_qr_code_layer(card, layer, data)
                    draw = ImageDraw.Draw(card)
                else:
                    logger.warning(f"Unknown layer type '{layer_type}' for layer {layer.get('id')}")
            except Exception as e:
                logger.error(f"FAILED to render {layer_type} layer {layer.get('id')}: {e}", exc_info=True)
        
        return card
    
    def render_both_sides(
        self,
        template: Dict[str, Any],
        data: Dict[str, Any],
        photo_image: Optional[Image.Image] = None,
    ) -> Tuple[Image.Image, Image.Image]:
        """
        Render both front and back of an ID card.
        
        Returns:
            Tuple of (front_image, back_image)
        """
        front = self.render(template, data, photo_image, 'front')
        back = self.render(template, data, photo_image, 'back')
        return front, back


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def load_template_from_db(template_id: int) -> Optional[Dict[str, Any]]:
    """Load a template from the database."""
    from app.db.database import db_manager
    
    query = """
        SELECT id, name, template_type, school_level, is_active,
               canvas, front_layers, back_layers,
               created_at, updated_at
        FROM id_templates
        WHERE id = %s
    """
    
    row = db_manager.execute_query(query, (template_id,), fetch_one=True)
    
    if not row:
        return None
    
    # Parse JSON fields
    front_data = row.get('front_layers', '{}')
    back_data = row.get('back_layers', '{}')
    canvas_data = row.get('canvas', '{}')
    
    if isinstance(front_data, str):
        front_data = json.loads(front_data)
    if isinstance(back_data, str):
        back_data = json.loads(back_data)
    if isinstance(canvas_data, str):
        canvas_data = json.loads(canvas_data)
    if not isinstance(canvas_data, dict):
        canvas_data = {}
    
    return {
        'id': row['id'],
        'templateName': row['name'],
        'templateType': row['template_type'],
        'schoolLevel': row['school_level'],
        'isActive': row['is_active'],
        'canvas': {
            'width': canvas_data.get('width', 1016),
            'height': canvas_data.get('height', 638),
            'backgroundColor': canvas_data.get('backgroundColor', '#FFFFFF'),
            'backgroundImage': canvas_data.get('backgroundImage'),
        },
        'front': front_data,
        'back': back_data,
        'metadata': {
            'version': row.get('version', '1.0'),
        }
    }


def load_active_template(template_type: str = 'student') -> Optional[Dict[str, Any]]:
    """Load the active template for a given type."""
    from app.db.database import db_manager
    
    # Simple query: Find ANY active template
    # We don't filter by template_type because only ONE template should be active at a time
    query = """
        SELECT id, name, template_type, school_level, is_active,
               canvas, front_layers, back_layers,
               created_at, updated_at
        FROM id_templates
        WHERE is_active = 1
        LIMIT 1
    """
    
    row = db_manager.execute_query(query, None, fetch_one=True)
    
    if not row:
        logger.error("CRITICAL: No active template found in database. Please activate a template in the Editor.")
        return None
    
    logger.info(f"✓ Loaded active template: {row['name']} (ID: {row['id']}, Type: {row['template_type']})")
    
    # Parse JSON fields
    front_data = row.get('front_layers', '{}')
    back_data = row.get('back_layers', '{}')
    canvas_data = row.get('canvas', '{}')
    
    logger.debug(f"Raw front_data type: {type(front_data)}, length: {len(str(front_data))}")
    logger.debug(f"Raw back_data type: {type(back_data)}, length: {len(str(back_data))}")
    
    if isinstance(front_data, str):
        front_data = json.loads(front_data)
    if isinstance(back_data, str):
        back_data = json.loads(back_data)
    if isinstance(canvas_data, str):
        canvas_data = json.loads(canvas_data)
    if not isinstance(canvas_data, dict):
        canvas_data = {}
    
    # Validate structure
    if not isinstance(front_data, dict) or not isinstance(back_data, dict):
        logger.error(f"INVALID template structure! front_data: {type(front_data)}, back_data: {type(back_data)}")
        return None
    
    front_bg = front_data.get('backgroundImage')
    back_bg = back_data.get('backgroundImage')
    front_layers = front_data.get('layers', [])
    back_layers = back_data.get('layers', [])
    
    logger.info(f"Template structure: Front BG={bool(front_bg)}, Front Layers={len(front_layers)}, Back BG={bool(back_bg)}, Back Layers={len(back_layers)}")
    
    return {
        'id': row['id'],
        'templateName': row['name'],
        'templateType': row['template_type'],
        'schoolLevel': row['school_level'],
        'isActive': row['is_active'],
        'canvas': {
            'width': canvas_data.get('width', 1016),
            'height': canvas_data.get('height', 638),
            'backgroundColor': canvas_data.get('backgroundColor', '#FFFFFF'),
            'backgroundImage': canvas_data.get('backgroundImage'),
        },
        'front': front_data,
        'back': back_data,
        'metadata': {
            'version': row.get('version', '1.0'),
        }
    }
