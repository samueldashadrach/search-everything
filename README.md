# search-everything

Search everything you've done on your PC. Ask interesting questions and get interesting answers.

Some sample questions you can ask:
 - How can I reorganise my desktop?
 - What are some of my hidden interests I may not be aware of?
 - How can I improve my coding style?

[Link to examples](https://twitter.com/casimir_five/status/1647240894439907331)

# How to use

Code will only work on Windows. (Tested on Windows 64 bit)

You will need to obtain google tesseract executable and store it in same directory for pytesseract to work.

https://towardsdatascience.com/read-text-from-image-with-one-line-of-python-code-c22ede074cac

https://github.com/UB-Mannheim/tesseract/wiki

All libraries can be installed from pip

You will require an OpenAI API key with support for GPT3 ada embeddings, and GPT4.

# How it works

While working:

1. Takes screenshots periodically.
2. Converts to text via OCR.
3. Obtains GPT3 ada embeddings (which can be stored locally).

When asking a question:

1. Uses embedding search on query to find top-n most relevant screenshots.
2. Sends text of top-n screenshots, and query, and a meta-prompt ("Here are some relevant screenshots ....") to GPT4 API. Prints response.

