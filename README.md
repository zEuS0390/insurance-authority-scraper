# 🌐 Insurance Authority Scraper

The project is an automated web scraper built to assist in obtaining large amounts of data from the https://iir.ia.org.hk/ website. By harnessing the power of automation, the web scraper is poised to significantly enhance productivity, empowering users with seamless access to comprehensive information. Please note that any data obtained from the website belongs to its owner. This project is funded by Tsz Ngong Conrad Ko.

## ❓ How to Use It?
Before running the program, make sure to download and install the following:

- **Geckodriver:** Download and install Geckodriver to enable Selenium to use the Firefox browser. You can download Geckodriver from [here](https://github.com/mozilla/geckodriver/releases). Make sure to place it in a directory included in your system's PATH environment variable.

- **Tesseract-OCR:** Install Tesseract-OCR to solve scan and read CAPTCHA images. You can find installation instructions on the [Tesseract-OCR GitHub page](https://github.com/UB-Mannheim/tesseract/wiki) for Windows. Ensure Tesseract-OCR is properly installed and accessible from the command line.

- **MongoDB Server:** Download and install the MongoDB server to store the data that was scraped from the website. You can download the MongoDB Server from [here](https://www.mongodb.com/try/download/community).

### 1. Create a Virtual Environment
In this project, we are using virtualenv to manage dependencies and the virtual environment. Before executing the following command to create the virtual environment, ensure that virtualenv is installed on your system. You can do this by running the following command in your terminal or command prompt:
```
pip show virtualenv
```

If virtualenv is installed, this command will display information about the installed package. If it's not installed, you can install it using pip:
```
pip install virtualenv
```

Once virtualenv is installed, navigate to the project folder and execute the following commands to create the virtual environment:
```
mkdir .venv/
```
```
python -m virtualenv .venv/
```

### 2. Activate the Virtual Environment
To activate the virtual environment, execute the following command in your terminal or command prompt:

If you're using command-prompt on Windows, enter this command
```
".venv/Scripts/activate" 
```

If you're using terminal on Windows, enter this command
```
. .venv/Scripts/activate
```

If you're using Linux, enter this command
```
. .venv/bin/activate
```

### 3. Install the Required Dependencies
No need to worry about manual installation of dependencies because there is a provided requirements.txt file. Execute the following command from your project directory to install the required dependencies:
```
pip install -r requirements.txt
```

**The required dependencies are:**
- Selenium
- Pytesseract
- OpenCV
- PyMongo

### 4. Run the main entry point of the program
To start and run the main entry point of the program, execute the following command in your activated virtual environment:
```
python main.py
```
