import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ExifTags
from pillow_heif import register_heif_opener
from datetime import datetime
import math

register_heif_opener()

def add_rounded_rectangle(draw, position, radius, fill):
    upper_left_point = (position[0], position[1])
    bottom_right_point = (position[2], position[3])

    draw.rectangle(
        [upper_left_point[0] + radius, upper_left_point[1],
         bottom_right_point[0] - radius, bottom_right_point[1]], 
        fill=fill
    )
    draw.rectangle(
        [upper_left_point[0], upper_left_point[1] + radius,
         bottom_right_point[0], bottom_right_point[1] - radius], 
        fill=fill
    )
    draw.pieslice(
        [upper_left_point[0], upper_left_point[1],
         upper_left_point[0] + radius * 2, upper_left_point[1] + radius * 2],
        180, 270, 
        fill=fill
    )
    draw.pieslice(
        [bottom_right_point[0] - radius * 2, upper_left_point[1],
         bottom_right_point[0], upper_left_point[1] + radius * 2],
        270, 360, 
        fill=fill
    )
    draw.pieslice(
        [upper_left_point[0], bottom_right_point[1] - radius * 2,
         upper_left_point[0] + radius * 2, bottom_right_point[1]],
        90, 180, 
        fill=fill
    )
    draw.pieslice(
        [bottom_right_point[0] - radius * 2, bottom_right_point[1] - radius * 2,
         bottom_right_point[0], bottom_right_point[1]],
        0, 90, 
        fill=fill
    )

def ratio_size(x, img):
    max_width_height = max(img.width, img.height)
    return (x/4032)*max_width_height

def add_timestamp(directory, suffix="_ts", font_path="IBMPlexSans-Regular.ttf"):
    output_directory = os.path.join(directory, "timestamped")
    text_color = (235, 235, 235)
    photo_width = 6
    photo_height = 4

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.heic')):
            try:
                file_path = os.path.join(directory, filename)

                with Image.open(file_path) as img:
                    if filename.lower().endswith('.heic'):
                        img = img.convert('RGB')

                    # Ensure the image is in the correct orientation
                    img = ImageOps.exif_transpose(img)
                    
                    # created_time = os.path.getctime(file_path)
                    # this works on Mac only for now
                    created_time = os.stat(file_path).st_birthtime
                    created_datetime = datetime.fromtimestamp(created_time)
                    current_datetime = created_datetime.strftime("%a %b %d, %Y %-I:%M %p")

                    img = img.convert('RGBA')
                    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                    draw = ImageDraw.Draw(overlay)

                    font_size = max(16,math.ceil(ratio_size(70,img)))
                    font = ImageFont.truetype(font_path, font_size)
                    
                    bbox = draw.textbbox((0, 0), current_datetime, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    is_horizontal = img.width > img.height
                    

                    # Position text based on image orientation
                    if is_horizontal:
                        print_width = img.width
                        print_height = img.width*photo_height/photo_width
                        print_hoffset = (img.height - print_height) / 2

                        text_x = img.width - text_width - ratio_size(200,img)
                        text_y = img.height - text_height - print_hoffset - ratio_size(200,img)
                    else:
                        print_height = img.height
                        print_width = img.height*photo_height/photo_width
                        print_woffset = (img.width - print_width) / 2

                        text_x = img.width - text_width - print_woffset - ratio_size(200,img)
                        text_y = img.height - text_height - ratio_size(220,img)

                    text_position = (text_x, text_y)
                    
                    padding = max(10,math.ceil(ratio_size(26,img)))
                    background_position = (
                        text_position[0] - padding,
                        text_position[1] - padding/2,
                        text_position[0] + text_width + padding,
                        text_position[1] + text_height + 2*padding
                    )
                    
                    radius = max(4, ratio_size(20,img))  # Radius for the rounded corners
                    add_rounded_rectangle(draw, background_position, radius, (0, 0, 0, 50))
                    
                    # Composite the overlay with the original image
                    img = Image.alpha_composite(img, overlay)

                    # Convert back to RGB and draw the text over the background
                    img = img.convert('RGB')
                    draw = ImageDraw.Draw(img)
                    draw.text(text_position, current_datetime, font=font, fill=text_color)
                    
                    output_filename = f"{filename.rsplit('.', 1)[0]}{suffix}.jpg"
                    output_file_path = os.path.join(output_directory, output_filename)
                    
                    img.save(output_file_path, 'jpeg', quality=95)
                    print(f"Timestamp added to {output_filename}")
            except Exception as e:
                print(f"An error occurred with {filename}: {e}")

directory_path = "./pics"
add_timestamp(directory_path)
