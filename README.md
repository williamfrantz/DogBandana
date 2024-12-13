# Dog Bandana Image Generator

A Python application that allows users to create custom dog bandana designs by overlaying text on images or using different fonts to create text-based designs.

## Features

- Create text overlays on background images
- Generate text-based designs using various fonts
- Preview thumbnails in an image gallery
- Support for multiple image formats (PNG, JPG, JPEG, TIFF, BMP, GIF)
- Support for various font formats (TTF, OTF, TTC)
- Interactive GUI for design selection

## Requirements

- Python 3.x
- PIL (Python Imaging Library/Pillow)
- tkinter (usually comes with Python)

## Installation

1. Ensure Python 3.x is installed on your system
2. Install required dependencies: pip install Pillow


## Project Structure

The program consists of several main classes:

- `Graphic`: Handles individual images and text rendering
- `Overlay`: Manages the combination of background images and text
- `ImageLibrary`: Manages collections of images and fonts
- `ImageGallery`: Provides the GUI interface for image selection

## Usage

### Basic Usage

Create an instance of ImageLibrary by providing a directory containing images or fonts:

For images
```python
image_library = ImageLibrary("path/to/image/directory")
```

For text with fonts
```python
text_library = ImageLibrary("path/to/font/directory", "Your Text")
```

## Creating an Overlay

### Create an overlay with background and text
```python
background = Graphic("background.png")
text = Graphic("font.ttf", "Your Text")
overlay = Overlay(background, text)
```

### Get the final image
```python
final_image = overlay.getImage()
```

## Using the Image Gallery

```python
root = tk.Tk()
library = ImageLibrary("path/to/images")
gallery = ImageGallery(root, library)
gallery.pack()
root.mainloop()
```

## Customization

Default image size can be modified by changing the DEFAULTSIZE constant

Thumbnail sizes can be adjusted using setThumbnailSize()

Text scaling can be modified through the SCALEFACTOR parameter

## Supported File Types

- Images
  - PNG (.png)
  - JPEG (.jpg, .jpeg)
  - TIFF (.tiff)
  - BMP (.bmp)
  - GIF (.gif)
- Fonts
  - TrueType (.ttf)
  - OpenType (.otf)
  - TrueType Collection (.ttc)

## Notes

- The program automatically handles image resizing and text fitting

- Text is automatically centered on the image

- Images can be mirrored for printing using getPrintImage()

- The gallery interface automatically adjusts based on window size
