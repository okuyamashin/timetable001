import base64
import requests

def encode_image_to_base64(image_path):
    """Encode an image file to a Base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def upload_base64_image(image_path, server_url):
    """Upload an image as a Base64 string to the server."""
    encoded_image = encode_image_to_base64(image_path)
    
    payload = {
        "image_base64": encoded_image,
        "filename": image_path.split("/")[-1]
    }
    
    response = requests.post(server_url, json=payload)
    return response.json()

if __name__ == "__main__":
    image_path = "example.jpg"  # ここにアップロードしたい画像のパスを指定
    server_url = "http://your-server.com/upload"  # ここにサーバーのアップロードURLを指定
    
    response = upload_base64_image(image_path, server_url)
    print("Server Response:", response)

