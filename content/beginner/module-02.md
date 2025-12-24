# Module 2: Your First Conversations with Python

## 1. The Python Interpreter
We will use the Python language. It is clean, readable, and powerful.
When you installed Python, you installed an **interpreter**. This is a program that reads your text file and executes the commands inside it.

## 2. Hello, World!
The tradition for every programmer is to make the computer speak.
Open your text editor. Create a new file named `hello.py`.
Type this exactly:

```python
print("Hello, world!")
```

Save the file.
Open your terminal. Navigate to the folder where you saved the file.
Run it by typing:

```bash
python hello.py
```

(Or `python3 hello.py` on Mac/Linux).

**What happened?**
The computer printed `Hello, world!` to the screen.
You just gave a command, and the machine obeyed.

## 3. Breaking It Down
*   `print`: This is a **function**. A command built into Python.
*   `(...)`: Parentheses tell Python we are "calling" the function (using it).
*   `"Hello, world!"`: The text inside quotes is a **string**. It is the data we are passing to the function.

## 4. Common Mistakes
Try to break it on purpose. Change your file to this:

```python
print("Hello, world"
```

Run it. You will see:
`SyntaxError: unexpected EOF while parsing` (or similar).

This means "End Of File" came too soon. You forgot the closing `)`.
Fix it and run it again.

## 5. Comments
You can leave notes for yourself.

```python
# This is a comment. Python ignores it.
print("This code runs.") # This is also a comment.
# print("This code does NOT run because it is commented out.")
```

Use comments to explain *why* you did something, not *what* you did.
