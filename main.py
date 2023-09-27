import os
import uuid
import cv2
from flask import Flask, request, send_file, jsonify
from PIL import Image
from rembg import remove

app = Flask(__name__)


@app.route('/upload', methods=['POST'])
def upload():
    file_name = str(uuid.uuid4()) + '.jpg'
    images = request.files['file']
    remove_bg = request.form.get('remove')
    bg_fon = request.form.get('fon')
    custom_fon = request.form.get('custom_fon')

    if images is None:
        return jsonify({'error': 'No file selected'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400

    if not images.filename:
        return jsonify({'error': 'No file selected'}), 400

    if not images.filename.lower().endswith(('.jpg', '.png', '.jpeg')):
        return jsonify({'error': 'File type not allowed'}), 401

    images_directory = './images'
    images.save(os.path.join(images_directory, images.filename))

    global cropped
    image = cv2.imread(os.path.join(images_directory, images.filename))
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # print fase count
    print(f'Found {len(faces)} face(s)')
    if len(faces) == 0:
        print("Face not found")
        return jsonify({'error': 'Face not found'}), 402
        exit()

    if len(faces) > 2:
        faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)[:2]

    threshold = image.shape[1] // 2

    for i, (x, y, w, h) in enumerate(faces):
        if x > threshold:
            cropped = image[y - 130:y + h + 130, x - 130:x + w + 0]
            cv2.imwrite(f'./output/{file_name}', cropped)
            print("o'ng")
        elif x + w < threshold:
            cropped = image[y - 130:y + h + 130, x - 0:x + w + 130]
            cv2.imwrite(f'./output/{file_name}', cropped)
            print("chap")
        else:
            cropped = image[y - 130:y + h + 130, x - 130:x + w + 130]
            cv2.imwrite(f'./output/{file_name}', cropped)
            print("o'rtada")

    cv2.destroyAllWindows()

    if custom_fon == 'true':
        with open(f'./output/{file_name}', 'rb') as img_file:
            output_file = remove(img_file.read())
            bg_removed_filename = str(uuid.uuid4()) + '.png'
            bg_removed_file_path = os.path.join('./output', bg_removed_filename)
            with open(bg_removed_file_path, 'wb') as f:
                f.write(output_file)

        background_path = './fon/fon.png'
        Image.open(bg_removed_file_path).convert("RGBA").resize((600, 600)).save(bg_removed_file_path)
        background = Image.open(background_path).convert("RGBA")
        foreground = Image.open(bg_removed_file_path).convert("RGBA")
        # Image.open(bg_removed_file_path).convert("RGBA").resize((background.width, background.height)).save(bg_removed_file_path)
        background.paste(foreground, (0, 0), foreground)
        background.save(f'./output/{file_name}', format="png")
        send = send_file(f'./output/{file_name}', mimetype='image/png')
        os.remove(bg_removed_file_path)
        os.remove(os.path.join(images_directory, images.filename))
        os.remove(f'./output/{file_name}')
        return send

    if bg_fon == 'true':
        with open(f'./output/{file_name}', 'rb') as img_file:
            output_file = remove(img_file.read())
            bg_removed_filename = str(uuid.uuid4()) + '.png'
            bg_removed_file_path = os.path.join('./output', bg_removed_filename)
            with open(bg_removed_file_path, 'wb') as f:
                f.write(output_file)

        fon_color = '#ff0000'
        img = Image.open(bg_removed_file_path).convert("RGBA")
        new_bg = Image.new("RGBA", img.size, fon_color)
        img = Image.alpha_composite(new_bg, img)

        fon_img_path = os.path.join('./output', file_name)
        img.save(fon_img_path, "PNG")
        send = send_file(f'./output/{file_name}', mimetype='image/png')
        os.remove(bg_removed_file_path)
        os.remove(os.path.join(images_directory, images.filename))
        os.remove(fon_img_path)
        return send

    if remove_bg == 'true':
        with open(f'./output/{file_name}', 'rb') as img_file:
            output_file = remove(img_file.read())
            bg_removed_filename = str(uuid.uuid4()) + '.png'
            bg_removed_file_path = os.path.join('./output', bg_removed_filename)
            with open(bg_removed_file_path, 'wb') as f:
                f.write(output_file)
        send = send_file(bg_removed_file_path, mimetype='image/png')
        os.remove(bg_removed_file_path)
        os.remove(os.path.join(images_directory, images.filename))
        os.remove(f'./output/{file_name}')
        return send
    else:
        return send_file(f'./output/{file_name}', mimetype='image/jpeg')


@app.route('/')
def index():
    return "Hello World"


def main():
    app.run(host="0.0.0.0", port=2003, debug=True)


if __name__ == '__main__':
    main()
