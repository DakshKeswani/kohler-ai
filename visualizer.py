import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image

def generate_2d_floorplan(room_length, room_width, bundle_items, vastu_enabled, entrance_dir):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, room_length)
    ax.set_ylim(0, room_width)
    
    # Draw room boundaries
    ax.add_patch(patches.Rectangle((0, 0), room_length, room_width, fill=False, lw=3, color='black'))
    
    # Grid lines
    ax.grid(True, linestyle='-', alpha=0.3, color='#E2E4E9')
    
    GENERIC_LABELS = {
        "toilet": "Commode",
        "shower": "Shower Enclosure",
        "vanity": "Vanity & Basin",
        "mirror": "Wall Mirror"
    }

    for item in bundle_items:
        cat = item["category"]
        if cat == "faucet" or cat == "accessory": 
            continue
            
        px, py = item["x"], item["y"]
        pw, pd = item["w"], item["d"]
        simple_label = GENERIC_LABELS.get(cat, item["name"])
        
        img_filename = item.get("img_file", f"{cat}.png")
        img_path = os.path.join(base_dir, 'assets', img_filename)
        
        # Base bounding box
        rect = patches.Rectangle((px, py), pw, pd, linewidth=1.5, edgecolor='#B8860B', fill=False, zorder=2)
        ax.add_patch(rect)
        
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path).convert("RGBA")
                target_width_px = int(pw * 150)
                target_height_px = int(pd * 150)
                img = img.resize((target_width_px, target_height_px), Image.Resampling.LANCZOS)
                ax.imshow(img, extent=[px, px+pw, py, py+pd], zorder=3, alpha=0.95)
            except Exception as e:
                print(f"Resize error for {img_filename}: {e}")

       # REVERSED ANTI-OVERLAP LOGIC: Vanity ABOVE, Mirror BELOW
        if cat == "vanity":
            # Push vanity text safely ABOVE the entire fixture box
            text_y = py + pd + 0.1 
            va_alignment = 'bottom'
        elif cat == "mirror":
            # Drop mirror text deep BELOW the golden bounding box
            text_y = py - 0.1 
            va_alignment = 'top'
        else:
            # Standard offset for shower and commode
            text_y = py - 0.1 
            va_alignment = 'top'

        # Render the label text ONCE
        ax.text(
            px + pw / 2, text_y,
            f"{simple_label}\n({pw}' × {pd}')",
            ha='center', va=va_alignment, fontsize=7.5, color='#1A1A1A', weight='700', zorder=5
        )
    # Door Swing Clearance
    door_w = 2.5
    door_x, door_y = 0, 0
    theta1, theta2 = 0, 90
    
    if entrance_dir == "South":
        door_x, door_y = room_length / 2, 0
        theta1, theta2 = 0, 90
    elif entrance_dir == "North":
        door_x, door_y = room_length / 2, room_width
        theta1, theta2 = 180, 270
    elif entrance_dir == "East":
        door_x, door_y = room_length, room_width / 2
        theta1, theta2 = 90, 180
    elif entrance_dir == "West":
        door_x, door_y = 0, room_width / 2
        theta1, theta2 = 270, 360

    door_arc = patches.Arc((door_x, door_y), door_w * 2, door_w * 2, angle=0, theta1=theta1, theta2=theta2, color='#B8860B', linestyle='--', linewidth=1.5)
    ax.add_patch(door_arc)
    
    label_offset_x = 0.5 if entrance_dir in ["South", "North"] else (0.5 if entrance_dir == "West" else -1.5)
    label_offset_y = 0.5 if entrance_dir in ["East", "West"] else (0.5 if entrance_dir == "South" else -1.5)
    ax.text(door_x + label_offset_x, door_y + label_offset_y, f"Entry ({entrance_dir})", fontsize=7, color='#B8860B', weight='bold')

    ax.set_xlim(-1, room_length + 1)
    ax.set_ylim(-1, room_width + 1)
    ax.set_aspect('equal')
    ax.axis('off')
    
    vastu_text = "Vastu Shastra Zoning: ACTIVE" if vastu_enabled else "Standard Plumbing Zoning"
    ax.text(room_length/2, -0.8, vastu_text, ha='center', fontsize=8, color='#1A1A1A', style='italic')
    
    plt.tight_layout()
    return fig