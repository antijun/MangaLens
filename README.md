# Manga Translator

A web application for translating manga panels and pages automatically. The app uses computer vision and machine learning to detect text in manga images, translate it, and overlay the translations back onto the original image.

## Features

- Upload manga panels or pages
- Automatic text detection and extraction
- Automatic translation using DeepL API
- Text segmentation to separate text from background
- Manual editing of translations
- Multiple view modes (original, text-only, translated)
- Download translated images

## Tech Stack

### Backend
- Python Flask for RESTful API
- OpenAI for OCR and translation assistance
- DeepL for translation
- SickZil-Machine for text segmentation
- Pillow for image processing

### Frontend
- React with TypeScript
- Vite for fast development
- Mantine UI component library
- React Router for navigation
- Axios for API communication

## Project Structure

```
manga-translator/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── simplified_app.py      # Simplified version (no SickZil-Machine)
│   ├── main.py                # Original manga translation logic
│   ├── ocr.py                 # OCR functionality
│   ├── typesetting.py         # Text overlay functionality
│   ├── image_processing/      # Image processing modules
│   ├── translation/           # Translation modules
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Application pages/views
│   │   ├── services/          # API client services
│   │   └── App.tsx            # Main application component
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
└── output/                    # Output directory for processed images
```

## Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- API keys for DeepL and OpenAI (add to a .env file)

### Backend Setup
1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the backend directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   DEEPL_KEY=your_deepl_api_key
   ```

4. Run the backend:

   **Standard version** (requires SickZil-Machine setup):
   ```
   python app.py
   ```
   
   **Simplified version** (no SickZil-Machine dependency):
   ```
   python simplified_app.py
   ```

### Frontend Setup
1. Install dependencies:
   ```
   cd frontend
   npm install
   ```

2. Run the development server:
   ```
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`

## Running with the Simplified Backend

If you encounter issues with SickZil-Machine dependency, you can use the simplified version of the backend that bypasses the text segmentation step:

1. Run the simplified backend:
   ```
   cd backend
   python simplified_app.py
   ```

2. The simplified version doesn't have text detection but allows you to test the upload, translation, and UI functionality.

## Troubleshooting

### SickZil-Machine Issues
If you encounter errors related to SickZil-Machine:

1. Install the correct TensorFlow version:
   ```
   pip install tensorflow==1.15.0
   ```

2. Check if you have the required model files:
   ```
   cd backend
   python fix_models.py
   ```

3. Alternatively, use the simplified backend:
   ```
   python simplified_app.py
   ```

### Testing Components Individually
Use the provided test scripts to check each component:

```
python test_translation.py   # Test translation functionality
python test_core_functions.py  # Test all core functions 
```

## Usage

1. Upload a manga image using the home page
2. Wait for the processing to complete
3. View and edit translations in the editor
4. Download the final translated image

## License

MIT
