# PixelSqueeze Free v1.0.0 – Batch Image Compression Tool (Source Code + EXE)

PixelSqueeze Free v1.0.0 is a lightweight, portable desktop application for batch image compression.  
It allows you to compress images efficiently without visible quality loss, supporting multiple formats and modern workflows.

This repository includes:
- Full Python source code
- Prebuilt Windows executable available under the Releases section
- Free and open-source distribution (MIT License)

------------------------------------------------------------
WINDOWS DOWNLOAD (EXE)
------------------------------------------------------------

Download the latest Windows executable from GitHub Releases:

https://github.com/rogers-cyber/PixelSqueeze/releases

- No Python required
- Portable executable
- Free & open source

------------------------------------------------------------
FEATURES
------------------------------------------------------------

- File & Folder Selection — Add individual images or entire folders
- Drag & Drop Support — Quickly queue files and folders
- Multi-Format Compression
  - JPG / PNG / WEBP
- Adjustable JPG Quality (1–100)
- Skip Existing Files — Avoid overwriting outputs
- Preserve Folder Structure (optional)
- Live Progress Tracking
  - Progress bar
  - Files-per-second speed indicator
- Background Processing — UI stays responsive
- Modern Dark UI — Built with Tkinter + ttkbootstrap
- Auto-Open Output Folder after completion
- Clear All — Reset file list and counters instantly
- Portable & Lightweight — No installation required (EXE)

------------------------------------------------------------
REPOSITORY STRUCTURE
------------------------------------------------------------

PixelSqueeze/
├── PixelSqueeze.py
├── dist/
│   └── (empty or .gitkeep)
├── icon.ico
├── requirements.txt
├── README.md
└── LICENSE

------------------------------------------------------------
INSTALLATION (SOURCE CODE)
------------------------------------------------------------

1. Clone the repository:

git clone https://github.com/rogers-cyber/PixelSqueeze.git
cd PixelSqueeze

2. Install dependencies:

pip install pillow ttkbootstrap tkinterdnd2 pillow-heif

(Tkinter is included with standard Python installations.)

3. Run the app:

python PixelSqueeze.py

------------------------------------------------------------
HOW TO USE
------------------------------------------------------------

1. Add Images
   - Drag & drop files or folders
   - Or click Add Files / Add Folder

2. Configure Options
   - Select output format (JPG / PNG / WEBP)
   - Adjust JPG quality if applicable
   - Enable Skip Existing Files if desired

3. Select Output Folder
   - Click Select Output Folder

4. Start Compression
   - Click Compress
   - Monitor progress and speed in real time

5. Completion
   - Output folder opens automatically (optional)

------------------------------------------------------------
SUPPORTED FORMATS
------------------------------------------------------------

Input:
- PNG, JPG, JPEG, BMP, GIF
- TIFF, WEBP
- HEIC (optional via pillow-heif)

Output:
- JPG
- PNG
- WEBP

------------------------------------------------------------
DEPENDENCIES
------------------------------------------------------------

- Python 3.10+
- Pillow
- pillow-heif (optional for HEIC support)
- ttkbootstrap
- tkinterdnd2 (optional for drag & drop)
- Tkinter
- Threading / Queue

------------------------------------------------------------
NOTES
------------------------------------------------------------

- Designed for batch image compression
- Non-blocking UI for large image sets
- Portable EXE suitable for USB or offline use
- Ideal for creators, developers, and daily workflows

------------------------------------------------------------
ABOUT
------------------------------------------------------------

PixelSqueeze Free is an open-source desktop utility created for learning, customization, and everyday image compression needs.

You are free to:
- Study the source code
- Modify it
- Redistribute it
- Include it in your own projects (see license)

------------------------------------------------------------
LICENSE
------------------------------------------------------------

This project is licensed under the MIT License.

You are free to use, modify, and distribute this software,
including the source code and compiled executable,
with attribution.

See the LICENSE file for full details.
