#!/usr/bin/env python3
import os
from PIL import Image, ImageDraw

def split_and_clean(input_path, output_dir, margin=15):
    """
    Splits a 3x3 character sheet and cleans the edges to remove bleed-in from neighbors.
    """
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    os.makedirs(output_dir, exist_ok=True)
    
    img = Image.open(input_path).convert("RGB")
    width, height = img.size
    
    cell_w = width // 3
    cell_h = height // 3
    
    print(f"Image size: {width}x{height}")
    print(f"Cell size: {cell_w}x{cell_h}")
    
    act_count = 1
    for row in range(3):
        for col in range(3):
            left = col * cell_w
            top = row * cell_h
            right = left + cell_w
            bottom = top + cell_h
            
            # Crop the cell
            cell = img.crop((left, top, right, bottom))
            
            # Cleaning Logic: 
            # We want to clear the edges because characters might touch the cell boundaries.
            # We'll draw a white border around the cell to 'erase' any neighbor fragments.
            draw = ImageDraw.Draw(cell)
            
            # Draw white rectangles on the 4 edges
            # Top
            draw.rectangle([0, 0, cell_w, margin], fill="white")
            # Bottom
            draw.rectangle([0, cell_h - margin, cell_w, cell_h], fill="white")
            # Left
            draw.rectangle([0, 0, margin, cell_h], fill="white")
            # Right
            draw.rectangle([cell_w - margin, 0, cell_w, cell_h], fill="white")
            
            output_name = f"act{act_count}.png"
            output_path = os.path.join(output_dir, output_name)
            cell.save(output_path, "PNG")
            print(f"Saved cleaned {output_name}")
            act_count += 1

if __name__ == "__main__":
    input_file = "outputs/action.png"
    output_folder = "outputs"
    # Using a 20 pixel margin for safer cleaning of neighbor bleed
    split_and_clean(input_file, output_folder, margin=20)
