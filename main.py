import argparse
import os
import time
from PIL import Image, ImageDraw, ImageFont
import requests

# Configuration
OUTPUT_DIR = "screenshots"
FILE_EXTENSIONS = [
    ".txt", ".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".go",
    ".php", ".rb", ".rs", ".swift", ".kt", ".ts"
]
MAX_RETRIES = 3
FONT_SIZE = 15
PADDING = 20
LINE_SPACING = 5

def get_files_from_github(url, token=None, retries=MAX_RETRIES):
    """
    Fetches the list of files from a GitHub repository with retries.
    Args:
        url (str): The GitHub API URL for the repository's contents.
        token (str, optional): GitHub personal access token. Defaults to None.
        retries (int, optional): Number of retries. Defaults to MAX_RETRIES.
    Returns:
        list: A list of dictionaries, where each dictionary represents a file
              or directory. Returns None if the request fails.
    """
    headers = {"User-Agent": "GitHubScreenshoter"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch data from GitHub API for URL: {url}. Status code: {response.status_code}")
                print(f"Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        
        if attempt < retries - 1:
            print("Retrying in 1 second...")
            time.sleep(1)
    
    return None

def create_image_from_text(content, output_path):
    """
    Creates an image from the given text content.
    Args:
        content (str): The text content to render.
        output_path (str): The path to save the image to.
    """
    try:
        # Use a common monospaced font
        font = ImageFont.truetype("cour.ttf", FONT_SIZE)
    except IOError:
        print("Courier font not found, using default font.")
        font = ImageFont.load_default()

    lines = content.splitlines()
    
    # Calculate the required image size
    max_width = 0
    line_heights = []

    for line in lines:
        try:
            # getbbox is more accurate for calculating size
            bbox = font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
        except AttributeError: # Fallback for older Pillow versions
            line_width, line_height = font.getsize(line)

        if line_width > max_width:
            max_width = line_width
        line_heights.append(line_height)

    # Use an average line height for consistency
    avg_line_height = sum(line_heights) / len(line_heights) if line_heights else FONT_SIZE
    total_height = int((avg_line_height + LINE_SPACING) * len(lines))

    img_width = max_width + PADDING * 2
    img_height = total_height + PADDING * 2

    image = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(image)

    # Draw the text line by line
    y_text = PADDING
    for i, line in enumerate(lines):
        draw.text((PADDING, y_text), line, font=font, fill="black")
        y_text += avg_line_height + LINE_SPACING

    image.save(output_path)

def process_files(files, token, path=""):
    """
    Processes a list of files, creating an image for each text/code file.
    Args:
        files (list): A list of file information dictionaries from the GitHub API.
        token (str): GitHub personal access token.
        path (str): The current path in the repository.
    """
    for file_info in files:
        if file_info["type"] == "file" and any(file_info["name"].endswith(ext) for ext in FILE_EXTENSIONS):
            headers = {"User-Agent": "GitHubScreenshoter"}
            file_content_response = requests.get(file_info["download_url"], headers=headers)
            if file_content_response.status_code == 200:
                file_content = file_content_response.text
                if file_content.strip():  # Skip empty or whitespace-only files
                    output_dir = os.path.join(OUTPUT_DIR, path)
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir)
                    output_path = os.path.join(output_dir, f"{file_info['name']}.png")
                    print(f"Creating image for {os.path.join(path, file_info['name'])}...")
                    create_image_from_text(file_content, output_path)
                    print(f"Image saved to {output_path}")
            else:
                print(f"Failed to download file: {file_info['download_url']}. Status code: {file_content_response.status_code}")

        elif file_info["type"] == "dir":
            new_path = os.path.join(path, file_info["name"])
            sub_files = get_files_from_github(file_info["url"], token)
            if sub_files:
                process_files(sub_files, token, new_path)

def main():
    """
    Main function to run the GitHub Screenshoter tool.
    """
    parser = argparse.ArgumentParser(description="Create images of text and code files in a GitHub repository.")
    parser.add_argument("repo_url", help="The GitHub repository URL (e.g., https://github.com/user/repo).")
    parser.add_argument("--token", help="GitHub personal access token to avoid rate limiting.")
    args = parser.parse_args()

    repo_path = args.repo_url.replace("https://github.com/", "")
    api_url = f"https://api.github.com/repos/{repo_path}/contents"

    files = get_files_from_github(api_url, args.token)
    if files:
        process_files(files, args.token)

if __name__ == "__main__":
    main()
