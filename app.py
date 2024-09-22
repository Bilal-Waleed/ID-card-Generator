from flask import Flask, request, render_template, send_file
from PIL import Image, ImageDraw, ImageFont
import os
import tempfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        name = request.form['name']
        roll_no = request.form['roll_no']
        time_slot = request.form['time_slot']  # Get the time slot from the form
        user_image = request.files['user_image']

        # Use a temporary file to save the user-uploaded image
        user_image_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        user_image.save(user_image_temp.name)
        user_image_temp.close()
        user_image_path = user_image_temp.name

        # Define the ID card dimensions
        width = 600
        height = 400

        # Create a white background image
        image = Image.new("RGB", (width, height), "white")

        # Create a green outline
        draw = ImageDraw.Draw(image)
        draw.rectangle([(0, 0), (width, height)], outline="green", width=5)

        # Define font and size
        font_path = "content/font/arial.ttf"  # Make sure the font path is correct
        font_title = ImageFont.truetype(font_path, 24)
        font_content = ImageFont.truetype(font_path, 18)

        # Write "ID Card" in the top left corner
        draw.text((20, 20), "ID Card", fill="green", font=font_title)

        details = [
            ("Name: ", name),
            ("Roll No: ", roll_no),
            ("Distance learning:", " No"),
            ("City:", " Karachi"),
            ("Center:", " Bahria Auditorium"),
            ("Campus:", " Karsaz"),
            ("Day/Time:", f" Sunday - {time_slot}"),  # Updated to include selected time slot
            ("Batch:", " 61")
        ]

        x_offset = 30
        y_offset = 80
        line_height = 30  # Space between lines

        for label, value in details:
            draw.text((x_offset, y_offset), label, font=font_content, fill="green")
            draw.text((x_offset + draw.textbbox((0, 0), label, font=font_content)[2], y_offset), value, font=font_content, fill=(0, 0, 0))
            y_offset += line_height

        # Add watermark with increased transparency
        try:
            watermark = Image.open("content/piaic.png").convert("RGBA")
            watermark = watermark.resize((150, 150))
            alpha = watermark.split()[3]
            alpha = alpha.point(lambda p: p * 0.2)  # Reduce opacity by 80%
            watermark.putalpha(alpha)
            image.paste(watermark, (width // 2 - 75, height // 2 - 75), mask=watermark)
        except FileNotFoundError:
            print("Watermark not found at content/piaic.png")

        # Add user picture
        try:
            my_pic = Image.open(user_image_path).convert("RGB")
            my_pic = my_pic.resize((135, 135))
            pic_x = width - 170
            pic_y = 50
            image.paste(my_pic, (pic_x, pic_y))
            draw.rectangle([(pic_x - 5, pic_y - 5), (pic_x + 130 + 5, pic_y + 130 + 5)], outline="green", width=5)
        except FileNotFoundError:
            print("User picture not found")

        # Add barcode close to the picture
        try:
            barcode = Image.open("content/barcode.png").convert("RGB")
            barcode = barcode.resize((150, 130))
            barcode_x = width - 185
            barcode_y = 220
            image.paste(barcode, (barcode_x, barcode_y))
        except FileNotFoundError:
            print("Barcode not found at content/barcode.png")

        # Add a horizontal black line above the "Authorized Signature" text
        line_y = barcode_y + barcode.height + 5  # Position the line below the barcode
        draw.line([(barcode_x, line_y), (barcode_x + 160, line_y)], fill="black", width=2)

        # Add text directly under the barcode
        text_x = barcode_x
        text_y = line_y + 5  # Place text just below the line
        draw.text((text_x, text_y), "Authorized Signature", fill="green", font=font_content)

        # Red and green boxes at the bottom
        box_width = 100
        box_height = 30
        box_y_position = height - box_height - 6

        # Red box
        red_box_x = 5
        draw.rectangle([(red_box_x, box_y_position), (red_box_x + box_width, box_y_position + box_height)], fill="red")
        draw.text((red_box_x + 15, box_y_position + 5), "Q1", fill="white", font=font_content)

        # Green box next to the red box
        green_box_x = red_box_x + box_width
        draw.rectangle([(green_box_x, box_y_position), (green_box_x + box_width, box_y_position + box_height)], fill="green")
        draw.text((green_box_x + 10, box_y_position + 5), "WMD", fill="white", font=font_content)

        # Save the generated ID card to a temporary file
        id_card_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image.save(id_card_temp.name)
        id_card_temp.close()

        return send_file(id_card_temp.name, as_attachment=True)

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
