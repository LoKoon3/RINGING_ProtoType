"""
RINGING - Frozen Silence Graphic Assets Generator
Based on the Frozen Silence design philosophy
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import random
import math
import os

# Create output directory
output_dir = os.path.dirname(os.path.abspath(__file__))
backgrounds_dir = os.path.join(output_dir, 'backgrounds')
textures_dir = os.path.join(output_dir, 'textures')
os.makedirs(backgrounds_dir, exist_ok=True)
os.makedirs(textures_dir, exist_ok=True)

# Frozen Silence Color Palette
COLORS = {
    'deep_black': (15, 18, 25),
    'charcoal': (35, 40, 50),
    'slate': (70, 80, 95),
    'ash': (110, 120, 130),
    'fog': (160, 170, 180),
    'snow_white': (220, 225, 230),
    'earth_brown': (60, 45, 35),
    'rust': (90, 60, 45),
    'amber': (180, 140, 60),
    'cold_blue': (80, 100, 130),
}

def add_noise(img, intensity=15):
    """Add film grain/noise texture"""
    pixels = img.load()
    width, height = img.size
    for i in range(width):
        for j in range(height):
            r, g, b = pixels[i, j][:3]
            noise = random.randint(-intensity, intensity)
            r = max(0, min(255, r + noise))
            g = max(0, min(255, g + noise))
            b = max(0, min(255, b + noise))
            if len(pixels[i, j]) == 4:
                pixels[i, j] = (r, g, b, pixels[i, j][3])
            else:
                pixels[i, j] = (r, g, b)
    return img

def create_gradient(width, height, color1, color2, direction='vertical'):
    """Create smooth gradient"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    for i in range(height if direction == 'vertical' else width):
        ratio = i / (height if direction == 'vertical' else width)
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)

        if direction == 'vertical':
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        else:
            draw.line([(i, 0), (i, height)], fill=(r, g, b))

    return img

def draw_building_silhouette(draw, x, width, height, base_y, color):
    """Draw a building silhouette with weathered edges"""
    # Random building shape
    building_height = random.randint(height // 4, height // 2)
    top_y = base_y - building_height

    # Main building body
    points = [(x, base_y), (x, top_y)]

    # Add irregular top
    num_segments = random.randint(3, 8)
    segment_width = width / num_segments
    for i in range(num_segments + 1):
        seg_x = x + i * segment_width
        seg_y = top_y + random.randint(-20, 30)
        points.append((seg_x, seg_y))

    points.append((x + width, base_y))

    draw.polygon(points, fill=color)

    # Add windows (sparse, some lit)
    window_rows = random.randint(3, 8)
    window_cols = random.randint(2, 5)
    for row in range(window_rows):
        for col in range(window_cols):
            if random.random() < 0.3:  # 30% chance of window
                wx = x + 10 + col * (width - 20) // window_cols
                wy = top_y + 20 + row * (building_height - 40) // window_rows
                ww, wh = 8, 12

                # Most windows dark, few lit with amber
                if random.random() < 0.1:
                    window_color = COLORS['amber']
                else:
                    window_color = tuple(max(0, c - 15) for c in color)

                draw.rectangle([wx, wy, wx + ww, wy + wh], fill=window_color)

def create_scene_background(scene_name, scene_config):
    """Create a scene background image"""
    width, height = 640, 1200  # Mobile portrait

    # Base gradient (sky)
    sky_top = scene_config.get('sky_top', COLORS['charcoal'])
    sky_bottom = scene_config.get('sky_bottom', COLORS['slate'])
    img = create_gradient(width, height, sky_top, sky_bottom)
    draw = ImageDraw.Draw(img)

    # Add atmospheric haze layers
    for layer in range(3):
        haze_y = height // 3 + layer * 100
        haze_alpha = 30 + layer * 20
        haze_color = (*COLORS['fog'], haze_alpha)

        # Create haze overlay
        haze = Image.new('RGBA', (width, 50), haze_color)
        haze = haze.filter(ImageFilter.GaussianBlur(radius=25))
        img.paste(haze.convert('RGB'), (0, haze_y), haze.split()[3] if haze.mode == 'RGBA' else None)

    # Draw distant buildings (lighter, more faded)
    ground_y = int(height * 0.7)
    for i in range(8):
        bx = random.randint(-50, width)
        bw = random.randint(40, 120)
        color_fade = tuple(min(255, c + 40) for c in COLORS['charcoal'])
        draw_building_silhouette(draw, bx, bw, height, ground_y - 50, color_fade)

    # Draw mid-ground buildings
    for i in range(6):
        bx = random.randint(-30, width - 50)
        bw = random.randint(60, 150)
        draw_building_silhouette(draw, bx, bw, height, ground_y, COLORS['charcoal'])

    # Draw foreground elements (darker)
    for i in range(4):
        bx = random.randint(-20, width - 100)
        bw = random.randint(80, 200)
        draw_building_silhouette(draw, bx, bw, height, ground_y + 100, COLORS['deep_black'])

    # Add snow on ground
    ground_color = scene_config.get('ground_color', COLORS['ash'])
    draw.rectangle([0, ground_y + 50, width, height], fill=ground_color)

    # Add scattered snow particles
    for _ in range(200):
        sx = random.randint(0, width)
        sy = random.randint(0, height)
        size = random.randint(1, 3)
        alpha = random.randint(100, 200)
        draw.ellipse([sx, sy, sx + size, sy + size], fill=(*COLORS['snow_white'][:3],))

    # Add noise for film grain effect
    img = add_noise(img, intensity=12)

    # Apply slight blur for atmospheric effect
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Save
    filepath = os.path.join(backgrounds_dir, f'{scene_name}.png')
    img.save(filepath, 'PNG', optimize=True)
    print(f'Created: {filepath}')
    return filepath

def create_ui_texture(name, width, height, base_color, style='rough'):
    """Create UI texture element"""
    img = Image.new('RGBA', (width, height), (*base_color, 255))
    draw = ImageDraw.Draw(img)

    if style == 'rough':
        # Add rough texture with random darker spots
        for _ in range(width * height // 20):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            darkness = random.randint(10, 40)
            color = tuple(max(0, c - darkness) for c in base_color)
            size = random.randint(1, 4)
            draw.ellipse([x, y, x + size, y + size], fill=(*color, 200))

    elif style == 'brushstroke':
        # Create horizontal brush stroke effect
        for y in range(height):
            variation = random.randint(-15, 15)
            color = tuple(max(0, min(255, c + variation)) for c in base_color)
            # Vary opacity across stroke
            alpha = 200 + random.randint(-30, 30)
            draw.line([(0, y), (width, y)], fill=(*color, alpha))

        # Add brush edge irregularity
        for _ in range(50):
            x = random.choice([random.randint(0, 10), random.randint(width - 10, width)])
            y = random.randint(0, height)
            draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(0, 0, 0, 0))

    elif style == 'inventory':
        # Dark textured background for inventory slots
        # Add radial gradient for depth
        center_x, center_y = width // 2, height // 2
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                max_dist = math.sqrt(center_x**2 + center_y**2)
                darkness = int(30 * (dist / max_dist))
                r = max(0, base_color[0] - darkness + random.randint(-5, 5))
                g = max(0, base_color[1] - darkness + random.randint(-5, 5))
                b = max(0, base_color[2] - darkness + random.randint(-5, 5))
                img.putpixel((x, y), (r, g, b, 255))

        # Add subtle highlight at top-left
        for i in range(20):
            alpha = int(30 * (1 - i / 20))
            draw.line([(i, 0), (0, i)], fill=(*COLORS['fog'], alpha))

    # Add noise
    img = add_noise(img, intensity=8)

    filepath = os.path.join(textures_dir, f'{name}.png')
    img.save(filepath, 'PNG', optimize=True)
    print(f'Created: {filepath}')
    return filepath

def create_brush_stroke_speaker():
    """Create brush stroke background for speaker name"""
    width, height = 200, 40
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Base brush stroke shape
    brush_color = COLORS['rust']

    # Draw main stroke with irregular edges
    for y in range(5, height - 5):
        # Vary width across the stroke
        progress = y / height
        wave = math.sin(progress * math.pi) * 0.3 + 0.7
        start_x = int(10 - wave * 8 + random.randint(-2, 2))
        end_x = int(width - 10 + wave * 8 + random.randint(-2, 2))

        # Color variation
        variation = random.randint(-10, 10)
        color = tuple(max(0, min(255, c + variation)) for c in brush_color)
        alpha = int(220 * wave) + random.randint(-20, 20)
        alpha = max(0, min(255, alpha))

        draw.line([(start_x, y), (end_x, y)], fill=(*color, alpha))

    # Add texture dots
    for _ in range(100):
        x = random.randint(15, width - 15)
        y = random.randint(8, height - 8)
        size = random.randint(1, 3)
        darkness = random.randint(-20, 20)
        color = tuple(max(0, min(255, c + darkness)) for c in brush_color)
        draw.ellipse([x, y, x + size, y + size], fill=(*color, 180))

    filepath = os.path.join(textures_dir, 'speaker_brush.png')
    img.save(filepath, 'PNG', optimize=True)
    print(f'Created: {filepath}')
    return filepath

def main():
    print("=== RINGING Frozen Silence Asset Generator ===\n")

    # Scene configurations
    scenes = {
        'scene_00_home': {
            'sky_top': COLORS['deep_black'],
            'sky_bottom': COLORS['charcoal'],
            'ground_color': COLORS['ash'],
        },
        'scene_01_street': {
            'sky_top': COLORS['charcoal'],
            'sky_bottom': COLORS['slate'],
            'ground_color': COLORS['fog'],
        },
        'scene_02_restarea': {
            'sky_top': COLORS['deep_black'],
            'sky_bottom': (50, 40, 35),  # Warm tint from fire
            'ground_color': COLORS['earth_brown'],
        },
        'scene_03_highway': {
            'sky_top': COLORS['slate'],
            'sky_bottom': COLORS['fog'],
            'ground_color': COLORS['snow_white'],
        },
        'scene_04_daejeon': {
            'sky_top': (20, 25, 40),  # Night blue
            'sky_bottom': COLORS['charcoal'],
            'ground_color': COLORS['ash'],
        },
        'scene_05_shelter': {
            'sky_top': COLORS['charcoal'],
            'sky_bottom': COLORS['slate'],
            'ground_color': COLORS['earth_brown'],
        },
        'scene_06_gyeongnam': {
            'sky_top': COLORS['slate'],
            'sky_bottom': COLORS['fog'],
            'ground_color': COLORS['snow_white'],
        },
        'scene_07_busan_outer': {
            'sky_top': COLORS['cold_blue'],
            'sky_bottom': COLORS['slate'],
            'ground_color': COLORS['ash'],
        },
        'scene_08_sanctuary': {
            'sky_top': COLORS['charcoal'],
            'sky_bottom': (60, 70, 90),  # Hint of hope
            'ground_color': COLORS['slate'],
        },
        'scene_09_ending': {
            'sky_top': (80, 70, 60),  # Dawn colors
            'sky_bottom': (120, 100, 80),
            'ground_color': COLORS['fog'],
        },
    }

    # Generate scene backgrounds
    print("Generating scene backgrounds...")
    for scene_name, config in scenes.items():
        create_scene_background(scene_name, config)

    # Generate UI textures
    print("\nGenerating UI textures...")

    # Inventory slot texture
    create_ui_texture('inv_slot', 64, 64, COLORS['earth_brown'], style='inventory')
    create_ui_texture('inv_slot_empty', 64, 64, (30, 25, 20), style='inventory')

    # Button textures
    create_ui_texture('btn_texture', 280, 50, COLORS['earth_brown'], style='rough')
    create_ui_texture('btn_texture_hover', 280, 50, COLORS['rust'], style='rough')

    # Sound box texture
    create_ui_texture('soundbox_texture', 300, 150, (40, 50, 65), style='rough')

    # Main text box background
    create_ui_texture('textbox_bg', 300, 200, (10, 12, 18), style='rough')

    # Speaker brush stroke
    create_brush_stroke_speaker()

    print("\n=== Asset generation complete! ===")
    print(f"Backgrounds saved to: {backgrounds_dir}")
    print(f"Textures saved to: {textures_dir}")

if __name__ == '__main__':
    main()
