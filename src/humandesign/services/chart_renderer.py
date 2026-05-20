# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-DevAIble-Commercial
#
# Human Design API
# Copyright (C) 2026 Dogan Turkuler <dogan.turkuler@gmail.com>
# https://devaible.com
#
# This file is part of Human Design API, available under dual license:
#   - AGPL-3.0 (open source): see LICENSE-AGPL
#   - Commercial License: see LICENSE-COMMERCIAL or contact dogan.turkuler@gmail.com

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.transforms
import matplotlib.patheffects as pe
from matplotlib.path import Path
from svgpath2mpl import parse_path
import json
import importlib.resources
import numpy as np

import io

# Import gate-to-center mapping for conditional text coloring
from ..features.mechanics import full_dict as mechanics_full_dict

# Build gate-to-center mapping from mechanics
GATE_TO_CENTER_MAP = mechanics_full_dict.get("full_gate_chakra_dict", {})

# --- 1. CONFIGURATION ---
LAYOUT_FILE = "layout_data.json"
OUTPUT_FILE = "bodygraph_output.png"

# Colors
COLOR_UNDEFINED = "#FFFFFF" # Pure White
COLOR_STROKE = "black"
COLOR_RED = "#DC143C"      # Crimson
COLOR_BLACK = "black"
COLOR_BODY_BG = "#E6E6E6"  # Darker gray vertical background for better contrast with white centers

# Premium Modern UI Color Palette
CENTER_COLORS = {
    "Head": "#FDF1AD",       # Soft Yellow
    "Ajna": "#719C91",       # Muted Teal
    "Throat": "#5B4B49",     # Dark Charcoal/Brown
    "G": "#FDF1AD",          # Soft Yellow (G Center)
    "G_Center": "#FDF1AD",   # Soft Yellow (alias)
    "Heart": "#D45656",      # Soft UI Red
    "Spleen": "#5B4B49",     # Dark Charcoal/Brown
    "SolarPlexus": "#5B4B49", # Dark Charcoal/Brown
    "Sacral": "#D45656",     # Soft UI Red
    "Root": "#5B4B49"        # Dark Charcoal/Brown
}

# Canvas Size (Matched to XAML ViewBox/Canvas)
# XAML Canvas is 240x320. 
CANVAS_W = 240
CANVAS_H = 320

# --- Helper to load JSON layout ---

def load_json_layout():
    """
    Loads the SVG layout data from layout_data.json using importlib.resources.
    """
    try:
        data_path = importlib.resources.files("humandesign.data").joinpath(LAYOUT_FILE)
        with data_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading layout file: {e}")
        return {}

def svg_to_mpl_path(svg_d):
    """Converts an SVG path string 'd' to a Matplotlib Path object."""
    if not svg_d:
        return None
    # svgpath2mpl works great usually.
    return parse_path(svg_d)


def get_parallel_offset_path(path, offset_distance):
    """
    Creates a parallel offset path by shifting vertices perpendicular to the path direction.
    
    For each segment, computes the normal vector and offsets all points (vertices and control points)
    by the specified distance. Works with Lines (LINETO), Cubic Bezier (CURVE4), and Quadratic Bezier (CURVE3).
    
    Args:
        path: A matplotlib.path.Path object
        offset_distance: Distance to offset (positive = right side when walking along path)
    
    Returns:
        A new matplotlib.path.Path with offset vertices
    """
    if path is None or len(path.vertices) < 2:
        return path
    
    vertices = path.vertices.copy()
    codes = path.codes.copy() if path.codes is not None else np.full(len(vertices), Path.LINETO)
    
    # Ensure first point is MOVETO
    if len(codes) > 0:
        codes[0] = Path.MOVETO
    
    # Compute offset for each vertex based on the local path direction
    offset_vertices = vertices.copy()
    
    i = 0
    while i < len(vertices):
        code = codes[i]
        
        if code == Path.MOVETO:
            # MOVETO: offset based on the direction to the next point
            if i + 1 < len(vertices):
                dx = vertices[i + 1, 0] - vertices[i, 0]
                dy = vertices[i + 1, 1] - vertices[i, 1]
                length = np.sqrt(dx * dx + dy * dy)
                if length > 0:
                    # Perpendicular normal (rotated 90° clockwise for positive offset)
                    nx = dy / length * offset_distance
                    ny = -dx / length * offset_distance
                    offset_vertices[i, 0] = vertices[i, 0] + nx
                    offset_vertices[i, 1] = vertices[i, 1] + ny
            i += 1
            
        elif code == Path.LINETO:
            # LINETO: offset based on direction from previous to current
            if i > 0:
                dx = vertices[i, 0] - vertices[i - 1, 0]
                dy = vertices[i, 1] - vertices[i - 1, 1]
                length = np.sqrt(dx * dx + dy * dy)
                if length > 0:
                    nx = dy / length * offset_distance
                    ny = -dx / length * offset_distance
                    offset_vertices[i, 0] = vertices[i, 0] + nx
                    offset_vertices[i, 1] = vertices[i, 1] + ny
            i += 1
            
        elif code == Path.CURVE4:
            # Cubic Bezier: 3 control points + 1 end point (4 vertices total)
            if i + 3 < len(vertices):
                # Get segment start (either MOVETO point or previous segment end)
                if i > 0:
                    start_x, start_y = vertices[i - 1]
                else:
                    start_x, start_y = vertices[i]
                
                # Compute direction from start to end for normal estimation
                end_x, end_y = vertices[i + 3]
                dx = end_x - start_x
                dy = end_y - start_y
                length = np.sqrt(dx * dx + dy * dy)
                
                if length > 0:
                    nx = dy / length * offset_distance
                    ny = -dx / length * offset_distance
                    
                    # Offset all 4 points of the curve
                    for j in range(4):
                        offset_vertices[i + j, 0] = vertices[i + j, 0] + nx
                        offset_vertices[i + j, 1] = vertices[i + j, 1] + ny
            i += 4
            
        elif code == Path.CURVE3:
            # Quadratic Bezier: 2 control points + 1 end point (3 vertices total)
            if i + 2 < len(vertices):
                # Get segment start
                if i > 0:
                    start_x, start_y = vertices[i - 1]
                else:
                    start_x, start_y = vertices[i]
                
                # Compute direction from start to end
                end_x, end_y = vertices[i + 2]
                dx = end_x - start_x
                dy = end_y - start_y
                length = np.sqrt(dx * dx + dy * dy)
                
                if length > 0:
                    nx = dy / length * offset_distance
                    ny = -dx / length * offset_distance
                    
                    # Offset all 3 points of the curve
                    for j in range(3):
                        offset_vertices[i + j, 0] = vertices[i + j, 0] + nx
                        offset_vertices[i + j, 1] = vertices[i + j, 1] + ny
            i += 3
            
        else:
            # For other codes, copy vertex as-is and advance
            i += 1
    
    return Path(offset_vertices, codes)


def draw_chart(chart_data, layout_data):
    # Setup Figure conforming to the aspect ratio
    fig, ax = plt.subplots(figsize=(8, 10.6), dpi=150) # Approx 240x320 ratio
    ax.set_xlim(0, CANVAS_W)
    ax.set_ylim(CANVAS_H, 0) # Flip Y axis because SVG/Canvas is top-left origin
    ax.axis('off')
    
    # 1. DRAW BODY OUTLINE
    body_d = layout_data.get('body_outline', "")
    if body_d:
        path = svg_to_mpl_path(body_d)
        patch = patches.PathPatch(path, facecolor=COLOR_BODY_BG, edgecolor='black', linewidth=0.8, zorder=0)
        ax.add_patch(patch)

    # 2. PREPARE DATA
    defined_centers = set(chart_data['general'].get('defined_centers', []))
    
    # Normalize center names to match layout keys
    # Map various naming conventions to the layout keys in layout_data.json
    center_name_mapping = {
        # Handle typos
        "Anja": "Ajna",
        # Handle space variations for Solar Plexus
        "Solar Plexus": "SolarPlexus",
        # Handle alternative names
        "Solar_Plexus": "SolarPlexus",
        "Ego": "Heart",
        "Plexo": "SolarPlexus",
        "Emocional": "SolarPlexus",
        "Spleen": "Spleen",
        "Splenic": "Spleen",
        # G-Center mapping (engine outputs "G_Center", layout uses "G")
        "G_Center": "G",
    }
    
    normalized_centers = set()
    for center in defined_centers:
        # Apply mapping if exists, otherwise keep original
        normalized_name = center_name_mapping.get(center, center)
        normalized_centers.add(normalized_name)
    defined_centers = normalized_centers
        
    design_gates = {g['Gate']: g for g in chart_data['gates']['des']['Planets']}
    personality_gates = {g['Gate']: g for g in chart_data['gates']['prs']['Planets']}
    
    # 3. DRAW CHANNELS / GATES
    # Draw active gates and full channels
    
    channels_layout = layout_data.get('channels', {})
    
    for gate_id_str, geo_data in channels_layout.items():
        gate_id = int(gate_id_str)
        
        path_d = geo_data.get('channel_path')
        if not path_d:
            continue
        mpl_path = svg_to_mpl_path(path_d)
        
        # 1. Draw Inactive state (Gray Background)
        patch_bg = patches.PathPatch(mpl_path, facecolor='none', edgecolor="#D3D3D3", linewidth=5, 
                                     capstyle='round', joinstyle='round', zorder=0.5)
        ax.add_patch(patch_bg)

        # Check activation
        is_design = gate_id in design_gates
        is_personality = gate_id in personality_gates
        
        if not (is_design or is_personality):
            continue
            
        z_order = 1
        
        if is_design and is_personality:
            # Dual-activation: Flush side-by-side rendering with unit-decoupled offset
            # line_width is in typographical points (for matplotlib linewidth)
            # data_offset is in data coordinates (for path transformation)
            line_width = 2.5  # Half of total 5px width (in points)
            data_offset = 0.45  # Empirical offset in data units to match visual width
            
            # Generate offset paths using data coordinates
            path_red = get_parallel_offset_path(mpl_path, -data_offset)
            path_black = get_parallel_offset_path(mpl_path, data_offset)
            
            # Draw Design (Red) on the left - identical linewidth and round cap
            patch_red = patches.PathPatch(path_red, facecolor='none', edgecolor=COLOR_RED, linewidth=line_width,
                                          capstyle='round', joinstyle='round', zorder=z_order)
            ax.add_patch(patch_red)
            
            # Draw Personality (Black) on the right - identical linewidth and round cap
            patch_black = patches.PathPatch(path_black, facecolor='none', edgecolor=COLOR_BLACK, linewidth=line_width,
                                           capstyle='round', joinstyle='round', zorder=z_order + 0.1)
            ax.add_patch(patch_black)
        elif is_design:
            patch = patches.PathPatch(mpl_path, facecolor='none', edgecolor=COLOR_RED, linewidth=5, 
                                      capstyle='round', joinstyle='round', zorder=z_order)
            ax.add_patch(patch)
        elif is_personality:
            patch = patches.PathPatch(mpl_path, facecolor='none', edgecolor=COLOR_BLACK, linewidth=5, 
                                      capstyle='round', joinstyle='round', zorder=z_order)
            ax.add_patch(patch)

    # 4. DRAW CENTERS (On top of channels)
    centers_layout = layout_data.get('centers', {})
    
    # Map generic names to XAML keys if needed. 
    # Standardize center names to match layout keys
    
    for name, data in centers_layout.items():
        # Determine if defined - name already matches layout key
        is_defined = name in defined_centers
        
        # Get center-specific color or use undefined white
        # Premium UI: No borders (edgecolor='none' via linewidth=0)
        if is_defined:
            fill_c = CENTER_COLORS.get(name, "#D4AF37")  # Default gold fallback
            stroke_c = "none"  # No border for premium UI look
        else:
            fill_c = COLOR_UNDEFINED
            stroke_c = "none"  # No border for undefined centers
        
        z_order = 10
        
        if data['type'] == 'rect':
            # X/Y in XAML Canvas are Top-Left
            # Premium UI: No borders (linewidth=0)
            rect = patches.Rectangle((data['x'], data['y']), data['w'], data['h'], 
                                     linewidth=0, edgecolor='none', facecolor=fill_c, zorder=z_order)
            
            # Add subtle drop shadow to undefined Head center only
            # Shadow pushed up and right to outline the top edges
            if name == 'Head' and not is_defined:
                rect.set_path_effects([pe.SimplePatchShadow(offset=(1.5, 2.5), shadow_rgbFace='black', alpha=0.1), pe.Normal()])
            
            ax.add_patch(rect)
        elif data['type'] == 'path':
            path = svg_to_mpl_path(data['path'])
            # Premium UI: No borders (linewidth=0)
            patch = patches.PathPatch(path, facecolor=fill_c, edgecolor='none', linewidth=0, zorder=z_order)
            
            # Add subtle drop shadow to undefined Head center only
            # Shadow pushed up and right to outline the top edges
            if name == 'Head' and not is_defined:
                patch.set_path_effects([pe.SimplePatchShadow(offset=(1.5, 2.5), shadow_rgbFace='black', alpha=0.1), pe.Normal()])
            
            # Apply Transform if present
            transform_str = data.get('transform')
            if transform_str:
                # Parse "m11 m12 m21 m22 dx dy"
                # XAML: M11, M12, M21, M22, OffsetX, OffsetY
                # MPL Affine2D.from_values(a, b, c, d, e, f) matches this order: a=M11, b=M12...
                t_vals = [float(v) for v in transform_str.split()]
                if len(t_vals) == 6:
                    t = matplotlib.transforms.Affine2D.from_values(*t_vals)
                    # We must add the patch's transform to the data transform (ax.transData)
                    patch.set_transform(t + ax.transData)
            
            ax.add_patch(patch)

    # 5. DRAW GATE NUMBERS
    gate_coords = layout_data.get('gates_coords', {})
    
    # We should iterate through all 64 gates to display them
    for gate_id_str, pt in gate_coords.items():
        gate_id = int(gate_id_str)
        x, y = pt['x'], pt['y']
        
        # Check if gate is active to highlight
        is_active = (gate_id in design_gates) or (gate_id in personality_gates)
        
        # Premium UI: Active gates get fixed-size white circle + bold black text
        # Inactive gates get subtle grey text with no background
        if is_active:
            # Active: Draw fixed-size white circle behind text
            # Calculate center position (gate coordinates are top-left, adjust to center)
            circle_x = x + 3
            circle_y = y + 3
            circle_radius = 4  # Fixed radius for all gates (reduced from 5 for better spacing)
            
            # Draw white circle patch
            circle_patch = patches.Circle((circle_x, circle_y), radius=circle_radius, 
                                          facecolor='white', edgecolor='none', zorder=20)
            ax.add_patch(circle_patch)
            
            # Draw bold black text centered in the circle (higher zorder to sit on top)
            ax.text(circle_x, circle_y, str(gate_id), fontsize=8, fontweight='bold', 
                    ha='center', va='center', zorder=22, color='#000000', fontfamily='sans-serif')
        else:
            # Inactive: Conditional text color based on parent center definition
            # Get parent center for this gate (abbreviation like "AA", "TT", etc.)
            parent_center_abbr = GATE_TO_CENTER_MAP.get(gate_id)
            
            # Map abbreviation to full center name and normalize
            center_name_mapping = {
                "HD": "Head",
                "AA": "Ajna",
                "TT": "Throat",
                "GC": "G_Center",
                "G": "G_Center",
                "HT": "Heart",
                "SP": "SolarPlexus",
                "SN": "Spleen",
                "SL": "Sacral",
                "RT": "Root"
            }
            parent_center = center_name_mapping.get(parent_center_abbr, parent_center_abbr)
            
            # Check if parent center is defined
            # defined_centers is already normalized in the Prepare Data section
            is_parent_defined = parent_center in defined_centers
            
            # Set text color: white for inactive gates in defined centers, grey for undefined
            text_color = '#EEEEEE' if is_parent_defined else '#888888'
            
            # Use same center coordinates for consistency
            ax.text(x + 3, y + 3, str(gate_id), fontsize=7, 
                    ha='center', va='center', zorder=21, color=text_color, fontfamily='sans-serif')

    # 6. SIDE PANELS (Planets) - Optional but good for completeness
    # Draw simple lists on left/right outside the canvas w/ clipping off? 
    # Current setup is 240x320. Side panels would need more width.
    # Let's keep it simple and just draw the chart as requested.
    
    return fig

def generate_bodygraph_image(chart_data, fmt='svg'):
    """
    Generates the BodyGraph image and returns it as whitespace-trimmed bytes.
    fmt: 'png', 'svg', 'jpg', 'jpeg'
    """
    layout = load_json_layout()
    fig = draw_chart(chart_data, layout)
    
    buf = io.BytesIO()
    
    # JPG does not support transparency
    use_transparent = True
    if fmt.lower() in ['jpg', 'jpeg']:
        use_transparent = False
        # Optional: Set background to white explicitly if strictly needed, 
        # but matplotlib defaults to white usually.
        fig.patch.set_facecolor('white')

    fig.savefig(buf, format=fmt, bbox_inches='tight', pad_inches=0.1, transparent=use_transparent)
    plt.close(fig)
    buf.seek(0)
    return buf.read()
    
# --- EXECUTION ---
if __name__ == "__main__":
    # Test Data
    json_data = """
{
  "general": {
    "birth_date": "(1968, 2, 21, 11, 0)",
    "create_date": "(1967, 11, 26, 17, 14)",
    "energy_type": "Manifesting Generator",
    "strategy": "Wait to Respond",
    "signature": "Satisfaction",
    "not_self": "Frustration & Anger",
    "aura": "Open & Enveloping",
    "inner_authority": "Solar Plexus",
    "inc_cross": "The Right Angle Cross of the Sleeping Phoenix (1)",
    "profile": "2/4: Hermit Opportunist",
    "defined_centers": [
      "Heart",
      "Throat",
      "G_Center",
      "Root",
      "Sacral",
      "SolarPlexus",
      "Spleen"
    ],
    "undefined_centers": [
      "Anja",
      "Head"
    ],
    "definition": "Single Definition",
    "variables": {
      "top_right": "right",
      "bottom_right": "left",
      "top_left": "right",
      "bottom_left": "right"
    }
  },
  "gates": {
    "prs": {
      "Planets": [
        {
          "Planet": "Sun",
          "Lon": 331.75753719941173,
          "Gate": 55,
          "Line": 2,
          "Color": 5,
          "Tone": 3,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Earth",
          "Lon": 151.75753719941173,
          "Gate": 59,
          "Line": 2,
          "Color": 5,
          "Tone": 3,
          "Base": 4,
          "Ch_Gate": 6
        },
        {
          "Planet": "Moon",
          "Lon": 244.2310066060069,
          "Gate": 34,
          "Line": 5,
          "Color": 3,
          "Tone": 2,
          "Base": 4,
          "Ch_Gate": 20
        },
        {
          "Planet": "North_Node",
          "Lon": 19.86214145569654,
          "Gate": 51,
          "Line": 6,
          "Color": 1,
          "Tone": 2,
          "Base": 5,
          "Ch_Gate": 25
        },
        {
          "Planet": "South_Node",
          "Lon": 199.86214145569653,
          "Gate": 57,
          "Line": 6,
          "Color": 1,
          "Tone": 2,
          "Base": 5,
          "Ch_Gate": 34
        },
        {
          "Planet": "Mercury",
          "Lon": 320.0165669655236,
          "Gate": 49,
          "Line": 2,
          "Color": 2,
          "Tone": 2,
          "Base": 5,
          "Ch_Gate": 0
        },
        {
          "Planet": "Venus",
          "Lon": 301.3880299909544,
          "Gate": 60,
          "Line": 6,
          "Color": 3,
          "Tone": 1,
          "Base": 3,
          "Ch_Gate": 3
        },
        {
          "Planet": "Mars",
          "Lon": 3.209266367962246,
          "Gate": 25,
          "Line": 6,
          "Color": 2,
          "Tone": 5,
          "Base": 3,
          "Ch_Gate": 51
        },
        {
          "Planet": "Jupiter",
          "Lon": 150.7621456594904,
          "Gate": 59,
          "Line": 1,
          "Color": 5,
          "Tone": 1,
          "Base": 3,
          "Ch_Gate": 6
        },
        {
          "Planet": "Saturn",
          "Lon": 10.109142964480705,
          "Gate": 21,
          "Line": 1,
          "Color": 4,
          "Tone": 6,
          "Base": 2,
          "Ch_Gate": 0
        },
        {
          "Planet": "Uranus",
          "Lon": 178.23219618103448,
          "Gate": 6,
          "Line": 6,
          "Color": 6,
          "Tone": 6,
          "Base": 2,
          "Ch_Gate": 59
        },
        {
          "Planet": "Neptune",
          "Lon": 236.52059882399786,
          "Gate": 14,
          "Line": 3,
          "Color": 1,
          "Tone": 6,
          "Base": 3,
          "Ch_Gate": 0
        },
        {
          "Planet": "Pluto",
          "Lon": 172.0592318541099,
          "Gate": 47,
          "Line": 6,
          "Color": 3,
          "Tone": 3,
          "Base": 2,
          "Ch_Gate": 0
        }
      ]
    },
    "des": {
      "Planets": [
        {
          "Planet": "Sun",
          "Lon": 243.75753719926954,
          "Gate": 34,
          "Line": 4,
          "Color": 6,
          "Tone": 2,
          "Base": 3,
          "Ch_Gate": 20
        },
        {
          "Planet": "Earth",
          "Lon": 63.757537199269564,
          "Gate": 20,
          "Line": 4,
          "Color": 6,
          "Tone": 2,
          "Base": 3,
          "Ch_Gate": 57
        },
        {
          "Planet": "Moon",
          "Lon": 175.54009086572225,
          "Gate": 6,
          "Line": 4,
          "Color": 1,
          "Tone": 4,
          "Base": 5,
          "Ch_Gate": 59
        },
        {
          "Planet": "North_Node",
          "Lon": 27.398443914748626,
          "Gate": 3,
          "Line": 2,
          "Color": 1,
          "Tone": 4,
          "Base": 2,
          "Ch_Gate": 60
        },
        {
          "Planet": "South_Node",
          "Lon": 207.3984439147486,
          "Gate": 50,
          "Line": 2,
          "Color": 1,
          "Tone": 4,
          "Base": 2,
          "Ch_Gate": 0
        },
        {
          "Planet": "Mercury",
          "Lon": 226.7428052951088,
          "Gate": 1,
          "Line": 4,
          "Color": 5,
          "Tone": 3,
          "Base": 1,
          "Ch_Gate": 0
        },
        {
          "Planet": "Venus",
          "Lon": 198.03426226579404,
          "Gate": 57,
          "Line": 4,
          "Color": 1,
          "Tone": 4,
          "Base": 4,
          "Ch_Gate": 34
        },
        {
          "Planet": "Mars",
          "Lon": 296.05678504320747,
          "Gate": 61,
          "Line": 6,
          "Color": 4,
          "Tone": 6,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Jupiter",
          "Lon": 154.80087449484986,
          "Gate": 59,
          "Line": 5,
          "Color": 6,
          "Tone": 6,
          "Base": 3,
          "Ch_Gate": 6
        },
        {
          "Planet": "Saturn",
          "Lon": 5.792372444524146,
          "Gate": 17,
          "Line": 3,
          "Color": 1,
          "Tone": 2,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Uranus",
          "Lon": 178.5293431806214,
          "Gate": 46,
          "Line": 1,
          "Color": 2,
          "Tone": 5,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Neptune",
          "Lon": 234.44073840486212,
          "Gate": 43,
          "Line": 6,
          "Color": 6,
          "Tone": 4,
          "Base": 4,
          "Ch_Gate": 0
        },
        {
          "Planet": "Pluto",
          "Lon": 172.62001351206544,
          "Gate": 47,
          "Line": 6,
          "Color": 6,
          "Tone": 6,
          "Base": 5,
          "Ch_Gate": 0
        }
      ]
    }
  },
  "channels": {
    "Channels": [
      {
        "channel": "6/59: The Channel of Mating (A Design Focused on Reproduction)"
      },
      {
        "channel": "20/34: The Channel of Charisma (A Design of Thoughts Becoming Deeds)"
      },
      {
        "channel": "25/51: The Channel of Initiation (A Design of Needing to be First)"
      },
      {
        "channel": "34/57: The Channel of Power (A Design of an Archetype)"
      },
      {
        "channel": "3/60: The Channel of Mutation (Energy that Generates and Initiates)"
      },
      {
        "channel": "20/57: The Channel of the Brainwave (A Design of Penetrating Awareness)"
      }
    ]
  }
}
"""
    
    chart = json.loads(json_data)
    layout = load_json_layout()
    fig = draw_chart(chart, layout)
    fig.savefig(OUTPUT_FILE, bbox_inches='tight', pad_inches=0.1, transparent=True)
    fig.savefig(OUTPUT_FILE.replace('.png', '.svg'), bbox_inches='tight', pad_inches=0.1, transparent=True)
    print(f"Chart saved to {OUTPUT_FILE} and {OUTPUT_FILE.replace('.png', '.svg')}")
