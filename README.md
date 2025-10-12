# PDF Viewer

Professional cross-platform PDF viewer with advanced features including dual-page mode, smooth page flip animations, and zoom controls.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Dual Page Mode**: View single or two-page spreads with seamless switching
- **Smooth Animations**: Page flip transitions with perspective effects
- **Smart Rendering**: Lazy loading with minimal memory footprint
- **Full Navigation**: Keyboard shortcuts, mouse wheel, and drag-to-scroll support
- **Flexible Zoom**: Auto-fit mode and manual zoom (20%-600%)
- **Modern UI**: Dark theme with intuitive controls
- **Cross-Platform**: Native executables for Windows, Linux, and macOS

## Installation

### Download Pre-built Binaries

Download the latest release for your platform from the [Releases](../../releases) page:

- **Windows**: `PDF-Viewer-Windows.exe`
- **Linux**: `PDF-Viewer-Linux.bin`
- **macOS**: `PDF-Viewer-macOS.app`

### Run from Source

```bash
# Clone repository
git clone https://github.com/eminsk/pdf-viewer.git
cd pdf-viewer

# Install dependencies
pip install pymupdf pillow

# Run application
python main.py
```

## Usage

### Opening Files

- Click **📂 Open** button or press `Ctrl+O`
- Select a PDF file from the dialog

### Navigation

- **Next/Previous Page**: Arrow keys `←` `→` or toolbar buttons
- **Page Slider**: Drag slider or click to jump to specific page
- **Mouse Wheel**: Scroll vertically through pages

### View Modes

- **Dual Page**: Press `D` or click **📖 Dual** button
- **Fit Mode**: Press `F` or click **🗖 Fit** to auto-fit pages to window
- **Zoom In/Out**: Press `+`/`-` or use toolbar buttons

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+O` or `O` | Open file |
| `←` | Previous page |
| `→` | Next page |
| `+` or `Ctrl+=` | Zoom in |
| `-` or `Ctrl+-` | Zoom out |
| `F` | Toggle fit mode |
| `D` | Toggle dual page mode |

### Mouse Controls

- **Middle-click + Drag**: Pan/scroll view
- **Mouse Wheel**: Scroll vertically

## Technical Details

### Architecture

The application uses object-oriented design with the following components:

- **PDFViewer** class: Main Tkinter window and state management
- **Lazy Rendering**: Pages rendered on-demand with caching
- **Animation System**: Frame-based page flip with easing
- **UI Framework**: ttk widgets with custom dark theme

### Dependencies

- **PyMuPDF** (fitz): PDF rendering engine
- **Pillow**: Image processing and transformations
- **tkinter**: Native GUI framework (included with Python)

### Performance

- **Memory**: ~50-100MB for typical PDFs (depends on page complexity)
- **Rendering**: Hardware-accelerated via PyMuPDF
- **Animation**: 30 FPS page flip transitions

## Development

### Requirements

- Python 3.12+
- PyMuPDF >= 1.26.4
- Pillow >= 11.3.0

### Project Structure

```
pdf-viewer/
├── main.py           # Main application
├── pyproject.toml    # Project metadata
├── README.md         # Documentation
└── .github/
    └── workflows/
        └── release.yml  # CI/CD automation
```

### Building from Source

#### Using Nuitka (Recommended)

```bash
# Install Nuitka
pip install nuitka

# Windows
python -m nuitka --standalone --enable-plugin=tk-inter --onefile main.py

# Linux/macOS
python -m nuitka --standalone --enable-plugin=tk-inter --onefile main.py
```

#### Manual Development

```bash
# Install dependencies
pip install pymupdf pillow

# Run application
python main.py
```

## Automated Releases

This project uses GitHub Actions for automated cross-platform builds. To create a release:

### Create Release Tag

```bash
# Tag version
git tag v0.1.0
git push origin v0.1.0
```

The CI/CD workflow automatically:
- Builds executables for Windows, Linux, and macOS
- Creates a GitHub release
- Attaches binaries to the release

### Manual Workflow Trigger

Navigate to: **Actions → Build and Release → Run workflow**

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Document complex logic with comments
- Keep methods focused and under 50 lines

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF rendering
- Uses [Pillow](https://python-pillow.org/) for image processing
- Inspired by modern document viewers

## Support

For issues, questions, or suggestions:

- Open an [Issue](../../issues)
- Check existing [Discussions](../../discussions)

## Roadmap

- [ ] Search functionality
- [ ] Bookmarks and annotations
- [ ] Text selection and copy
- [ ] Print support
- [ ] Dark/light theme toggle
- [ ] Recent files history
- [ ] Thumbnail sidebar

---

Made with ❤️ using Python and Tkinter
