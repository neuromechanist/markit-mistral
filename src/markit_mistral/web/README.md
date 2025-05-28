# MarkIt Mistral Web Interface

A browser-based interface for converting PDFs and images to markdown using Mistral AI, powered by PyScript for local processing.

## Features

- **Local Processing**: All file processing happens in your browser using PyScript
- **Privacy First**: Your API key and files never leave your browser
- **Drag & Drop**: Easy file upload with drag and drop support
- **Real-time Progress**: Live progress updates during processing
- **Math Support**: Preserves mathematical equations in LaTeX format
- **Image Extraction**: Extracts and downloads images from documents
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Modern web browser with JavaScript enabled
- Mistral AI API key ([Get one here](https://console.mistral.ai/))

### Using the Web Interface

1. **Open the Interface**
   - Open `index.html` in your web browser
   - Or serve it from a local web server

2. **Configure API Key**
   - Enter your Mistral API key in the configuration section
   - Your key is stored locally in browser storage for convenience
   - The key is never sent to any server except Mistral's API

3. **Upload a File**
   - Click the upload area or drag and drop a file
   - Supported formats: PDF, PNG, JPEG, TIFF
   - Maximum file size: 50MB

4. **Configure Options**
   - **Extract Images**: Include images from the document (enabled by default)
   - **Embed as Base64**: Embed images directly in markdown as base64

5. **Process Document**
   - Click "Process Document" to start
   - Watch the progress bar for real-time updates
   - Processing happens entirely in your browser

6. **Download Results**
   - **Download Markdown**: Get the generated markdown file
   - **Download Images**: Get extracted images as separate files
   - **Download All**: Get both markdown and images

## File Structure

```
web/
├── index.html              # Main web interface
├── static/
│   ├── main.js            # JavaScript UI logic
│   └── markit_web.py      # PyScript backend
└── README.md              # This file
```

## Technical Details

### Architecture

- **Frontend**: HTML5 + Tailwind CSS + Vanilla JavaScript
- **Backend**: Python running in browser via PyScript/Pyodide
- **API**: Direct calls to Mistral AI OCR API from browser

### Browser Compatibility

- Chrome/Chromium 90+
- Firefox 90+
- Safari 14+
- Edge 90+

### Security

- **Local Processing**: No server required, everything runs in your browser
- **API Key Storage**: Stored in browser's localStorage, never transmitted except to Mistral
- **File Privacy**: Files are processed locally and never uploaded to any intermediate server
- **HTTPS Required**: For security, serve over HTTPS in production

## Development

### Local Development

1. **Simple File Server**
   ```bash
   # Python 3
   python -m http.server 8000
   
   # Or using Node.js
   npx serve .
   ```

2. **Open in Browser**
   ```
   http://localhost:8000/index.html
   ```

### Customization

The interface can be customized by modifying:

- **Styling**: Edit the Tailwind classes in `index.html`
- **Functionality**: Modify `static/main.js` for UI behavior
- **Processing Logic**: Update `static/markit_web.py` for OCR processing

### Adding Features

To add new features:

1. Add UI elements to `index.html`
2. Add event handlers to `static/main.js`
3. Implement processing logic in `static/markit_web.py`
4. Update the communication between JS and Python

## Limitations

- **File Size**: 50MB maximum (Mistral API limit)
- **Internet Required**: Needs internet connection for Mistral API calls
- **Browser Memory**: Large files may consume significant browser memory
- **PyScript Loading**: Initial page load may be slower due to PyScript initialization

## Troubleshooting

### Common Issues

1. **"PyScript not loaded" error**
   - Ensure you have an internet connection for CDN resources
   - Try refreshing the page

2. **"Invalid API key" error**
   - Verify your Mistral API key is correct
   - Check if your API key has OCR permissions

3. **File upload not working**
   - Check file format is supported (PDF, PNG, JPEG, TIFF)
   - Ensure file is under 50MB
   - Try a different browser

4. **Processing stuck at 0%**
   - Check browser console for errors
   - Verify internet connection
   - Try with a smaller file

### Performance Tips

- **Large Files**: Break large PDFs into smaller chunks
- **Multiple Files**: Process files one at a time for best performance
- **Browser Memory**: Close other tabs when processing large files
- **Network**: Use on a stable internet connection for API calls

## Contributing

To contribute to the web interface:

1. Follow the main project's development workflow
2. Test changes in multiple browsers
3. Ensure responsive design works on mobile
4. Update this README for new features

## License

Same as the main MarkIt Mistral project (MIT License). 