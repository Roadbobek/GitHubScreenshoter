# GitHub Screenshoter

This tool takes screenshots of all text and code files in a GitHub repository.

## Prerequisites

- Python 3.x
- Google Chrome

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Road-b/GitHubScreenshoter.git
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download and install ChromeDriver from the official website.

## Usage

1. Run the `main.py` script with the GitHub repository URL as an argument:
   ```bash
   python main.py https://github.com/user/repo
   ```
2. To avoid API rate limiting, you can use a GitHub personal access token:
   ```bash
   python main.py https://github.com/user/repo --token YOUR_TOKEN
   ```
3. The screenshots will be saved in the `screenshots` directory.
