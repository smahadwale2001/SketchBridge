import base64
import os

def save_icon_to_text(file_path, output_file="enc.txt"):
    if not os.path.exists(file_path):
        print(f"Error: '{file_path}' not found! Make sure the image is in this folder.")
        return

    try:
        with open(file_path, "rb") as image_file:
            # Encode the image data
            encoded_bytes = base64.b64encode(image_file.read())
            encoded_string = encoded_bytes.decode('utf-8')
            
            # Write to enc.txt
            with open(output_file, "w") as f:
                f.write(encoded_string)
            
            print(f"✅ Success! Base64 string saved to {output_file}")
            print("Now open enc.txt, copy all text, and paste it into your TraceTiler class.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Ensure your image is named 'icon.png' or change the name below
    save_icon_to_text("icon.png")