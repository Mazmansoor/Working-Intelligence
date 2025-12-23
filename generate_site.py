import os

def write_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created {path}")

def get_relative_path(current_path, target_path):
    # current_path: e.g., 'beginner/module-01.html'
    # target_path: e.g., '/style.css' or '/beginner/'

    if target_path.startswith('http'):
        return target_path

    # Remove leading slash for relpath calculation
    target_clean = target_path.lstrip('/')

    # If target is root '/', it maps to '.' relative to root
    if target_path == '/':
        target_clean = '.'

    # Calculate relative path from the directory of current_path
    current_dir = os.path.dirname(current_path)
    if current_dir == '':
        current_dir = '.'

    # We want to go from current_dir to target_clean
    # But wait, target_clean is relative to root.
    # os.path.relpath(path, start) returns a relative filepath to path from start directory.

    # Example: current='beginner/mod1.html' (dir='beginner'), target='/style.css' (clean='style.css')
    # relpath('style.css', 'beginner') -> '../style.css'

    rel = os.path.relpath(target_clean, current_dir)

    # Ensure directory links end with / or index.html if needed, but standard hrefs usually don't need trailing slash if pointing to file.
    # If target was a directory (ended in /), we might want to preserve that or map to index.html?
    # The original links were like /path/ (implying index.html).
    # If I have relpath pointing to 'path', it might be better to point to 'path/index.html' explicitly for local file browsing,
    # or just 'path/' if serving via web server.
    # User said "links are not working", usually implies local file:// access issue or subfolder deployment.
    # Safe bet for file:// and GH pages: link to 'index.html' explicitly if it's a "folder" link.

    if target_path.endswith('/') and target_path != '/':
        # e.g. /path/ -> path -> relative is '../path' -> add '/index.html'
        # Check if we already have index.html in the rel path? No.
        # Let's just assume we link to index.html for directory links.
        rel = os.path.join(rel, 'index.html')
    elif target_path == '/':
         rel = os.path.join(rel, 'index.html')

    return rel

def get_template(title, content, current_page_path):
    # Navigation Structure
    # (Link Target, Link Text)
    nav_items = [
        ('/', 'Home'),
        ('/path/', 'The Path'),
        ('/beginner/', 'Beginner'),
        ('/learn/', 'Learn'),
        ('/build/', 'Build'),
        ('/reflections/', 'Reflections'),
        ('/about.html', 'About'),
    ]

    nav_html = ""
    for link_target, text in nav_items:
        rel_link = get_relative_path(current_page_path, link_target)

        # Determine active state
        # Simple check: if current page starts with the link directory (and link isn't root unless page is root)
        is_active = False
        if link_target == '/':
            if current_page_path == 'index.html':
                is_active = True
        else:
            # e.g. link=/beginner/, current=beginner/module-01.html
            # remove leading slash from link_target -> beginner/
            if current_page_path.startswith(link_target.lstrip('/')):
                is_active = True

        active_class = ' class="active"' if is_active else ''
        nav_html += f'<a href="{rel_link}"{active_class}>{text}</a>\n'

    # CSS Path
    css_rel = get_relative_path(current_page_path, '/style.css')

    # Fix internal content links
    # This is a bit hacky: we replace absolute hrefs in content with relative ones.
    # A robust solution would parse HTML, but simple string replacement for known paths works here.
    # We know the known paths are the keys in our pages dict + nav items.

    # Actually, simpler: define a helper to replace common paths
    def fix_content_links(html_content):
        # We need to replace href="/..." with relative versions.
        # Because we can't easily parse every random link, let's target the ones we know we generated.
        # The prompt generated content with hardcoded strings like href="/beginner/module-01.html".

        # Strategy: Find all href="..." and update them?
        # Or just replace the specific root folders.

        # Let's iterate over all known pages and replace their absolute path with relative.
        # And also the folder roots.

        # Sort by length descending to replace longest matches first (e.g. /beginner/module-01.html before /beginner/)

        replacements = {}

        # Add root folders
        folders = ['/path/', '/beginner/', '/learn/', '/build/', '/reflections/']
        for folder in folders:
            replacements[folder] = get_relative_path(current_page_path, folder)

        # Add root files
        replacements['/style.css'] = get_relative_path(current_page_path, '/style.css')
        replacements['/about.html'] = get_relative_path(current_page_path, '/about.html')
        replacements['/manifesto.html'] = get_relative_path(current_page_path, '/manifesto.html')
        replacements['/'] = get_relative_path(current_page_path, '/')

        # We also need to handle the generated pages links, e.g. /beginner/module-01.html
        # I'll populate this list dynamically in the main loop maybe?
        # For now, let's just do a generic replacement for href="/..."

        new_content = html_content

        # Crude but effective for this static content:
        # We manually listed all pages in the previous script.
        # Let's just fix the specific ones we used in the text.

        # A better way: Use a regex to find href="/..." and replace the match.
        import re
        def replace_link(match):
            full_match = match.group(0) # href="/..."
            url = match.group(1) # /...
            if url.startswith('/'):
                return f'href="{get_relative_path(current_page_path, url)}"'
            return full_match

        new_content = re.sub(r'href="(/[^"]*)"', replace_link, new_content)

        return new_content

    processed_content = fix_content_links(content)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Working Intelligence</title>
    <link rel="stylesheet" href="{css_rel}">
</head>
<body>
    <nav>
        {nav_html}
    </nav>
    <main>
        {processed_content}
    </main>
</body>
</html>
"""

pages = []

# --- Homepage ---
pages.append({
    'path': 'index.html',
    'title': 'Working Intelligence',
    'content': """
        <h1>Working Intelligence</h1>
        <p class="intro">Learning to Teach Machines — Slowly, Clearly, Honestly.</p>

        <p>A gentle path from Python to Machine Learning.<br>
        No hype. No shortcuts. No intimidation.</p>

        <br>
        <a href="/path/" class="cta-button">Start the Path</a>
    """
})

# --- The Path ---
pages.append({
    'path': 'path/index.html',
    'title': 'The Path',
    'content': """
        <h1>The Path</h1>
        <p class="intro">Understanding matters more than speed.</p>

        <h2>What is this learning journey?</h2>
        <p>This is a curriculum designed for absolute beginners who want to become real ML builders. It takes you from writing your first line of Python code to understanding the fundamental concepts behind modern AI.</p>

        <h2>Why slow?</h2>
        <p>Most tutorials rush you to "magic" results using complex libraries you don't understand. Here, we build concepts from the ground up. We make mistakes on purpose. We learn to debug. We learn to think.</p>

        <h2>How to use this site</h2>
        <p>Follow the modules in order. Do not copy-paste code. Type it out. Read the error messages. If you get stuck, take a break and come back. The goal is not to finish, but to understand.</p>

        <h2>Who is this for?</h2>
        <ul>
            <li>Absolute beginners to programming</li>
            <li>Curious professionals</li>
            <li>Future ML and AI builders</li>
        </ul>

        <p>It is <strong>not</strong> for those seeking quick hacks, certificates, or hype.</p>

        <br>
        <a href="/beginner/" class="cta-button">Begin Part I</a>
    """
})

# --- Beginner (Part I & II) ---
beginner_intro = """
    <h1>Beginner: Foundations</h1>
    <p class="intro">Learning to speak the language of the machine.</p>

    <p>We start at the very beginning. No prior knowledge is assumed.</p>

    <h2>Part I: Learning to Think in Steps</h2>
    <ul>
        <li><a href="/beginner/module-01.html">Module 1: What Programming Really Is</a></li>
        <li><a href="/beginner/module-02.html">Module 2: Your First Conversations with Python</a></li>
    </ul>

    <h2>Part II: Python Basics (Very Gentle)</h2>
    <ul>
        <li><a href="/beginner/module-03.html">Module 3: Variables and Simple Data</a></li>
        <li><a href="/beginner/module-04.html">Module 4: Asking Questions and Making Decisions</a></li>
        <li><a href="/beginner/module-05.html">Module 5: Repeating Work</a></li>
    </ul>
"""
pages.append({'path': 'beginner/index.html', 'title': 'Beginner Foundations', 'content': beginner_intro})

# Modules 1-5
pages.append({
    'path': 'beginner/module-01.html',
    'title': 'Module 1: What Programming Really Is',
    'content': """
        <h1>Module 1: What Programming Really Is</h1>

        <h2>Computers as Instruction Followers</h2>
        <p>Computers are not smart. They are incredibly fast, but they are literal. They do exactly what you tell them to do, not what you <em>meant</em> for them to do.</p>

        <h2>Precision vs Intention</h2>
        <p>Programming is the art of translating your vague human intention into precise machine instructions. If you want a robot to make a sandwich, "make a sandwich" is intention. "Pick up bread slice, place on counter, open peanut butter jar..." is precision.</p>

        <h2>Errors as Feedback</h2>
        <p>You will see red error messages. Many of them. This is not a failure. It is the computer saying, "I don't understand." Treat errors as helpful clues, not judgments.</p>

        <h2>Fear Removal</h2>
        <p>You cannot break the computer by writing code. Experiment. Type things. See what happens. The worst that happens is an error message.</p>

        <hr>
        <div class="module-nav">
            <a href="/beginner/">Back to Overview</a>
            <a href="/beginner/module-02.html">Next: Module 2 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'beginner/module-02.html',
    'title': 'Module 2: Your First Conversations with Python',
    'content': """
        <h1>Module 2: Your First Conversations with Python</h1>

        <h2>Running Python</h2>
        <p>Python is a language we use to talk to the computer. We write text (code), and an interpreter reads it and performs actions.</p>

        <h2>Printing</h2>
        <p>The simplest action is to show something on the screen.</p>
        <pre><code>print("Hello, world!")</code></pre>
        <p>This is your first program.</p>

        <h2>Comments</h2>
        <p>Code is for humans to read, too. We use comments to leave notes.</p>
        <pre><code># This is a comment. The computer ignores it.
print("This runs.")</code></pre>

        <h2>Reading Error Messages Calmly</h2>
        <p>If you type <code>print("Hello"</code> (missing parenthesis), Python will complain. Read the message. It often points to the exact line where the confusion happened.</p>

        <hr>
        <div class="module-nav">
            <a href="/beginner/module-01.html">&larr; Previous</a>
            <a href="/beginner/module-03.html">Next: Module 3 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'beginner/module-03.html',
    'title': 'Module 3: Variables and Simple Data',
    'content': """
        <h1>Module 3: Variables and Simple Data</h1>

        <h2>Numbers and Text</h2>
        <p>Computers work with data. Two basic types are numbers (like <code>42</code> or <code>3.14</code>) and text (strings, like <code>"Hello"</code>).</p>

        <h2>Naming (Variables)</h2>
        <p>A variable is a label for a value. It lets us store data to use later.</p>
        <pre><code>user_name = "Jules"
age = 25</code></pre>

        <h2>Reassignment</h2>
        <p>Variables can change.</p>
        <pre><code>age = 25
age = 26  # Now age refers to 26</code></pre>

        <h2>Why Types Matter</h2>
        <p>You can add two numbers: <code>2 + 2</code> is <code>4</code>. You can "add" two strings: <code>"A" + "B"</code> is <code>"AB"</code>. But you cannot add a number to a string. Python needs to know the type to know what to do.</p>

        <hr>
        <div class="module-nav">
            <a href="/beginner/module-02.html">&larr; Previous</a>
            <a href="/beginner/module-04.html">Next: Module 4 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'beginner/module-04.html',
    'title': 'Module 4: Asking Questions and Making Decisions',
    'content': """
        <h1>Module 4: Asking Questions and Making Decisions</h1>

        <h2>Input</h2>
        <p>Programs are more fun when they interact. We can ask the user for input.</p>
        <pre><code>name = input("What is your name? ")</code></pre>

        <h2>If / Else</h2>
        <p>We can make decisions based on data.</p>
        <pre><code>if age >= 18:
    print("You are an adult.")
else:
    print("You are a minor.")</code></pre>

        <h2>Comparisons</h2>
        <p>We use symbols to compare values: <code>==</code> (equal), <code>!=</code> (not equal), <code>&lt;</code>, <code>&gt;</code>.</p>

        <h2>Simple Validation</h2>
        <p>Always check if the input is what you expect. If you expect a number, check if the user actually typed a number.</p>

        <hr>
        <div class="module-nav">
            <a href="/beginner/module-03.html">&larr; Previous</a>
            <a href="/beginner/module-05.html">Next: Module 5 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'beginner/module-05.html',
    'title': 'Module 5: Repeating Work',
    'content': """
        <h1>Module 5: Repeating Work</h1>

        <h2>For Loops</h2>
        <p>If you want to do something a specific number of times, or for every item in a group, use a for loop.</p>
        <pre><code>for i in range(5):
    print("Hello")</code></pre>

        <h2>While Loops</h2>
        <p>If you want to repeat something <em>as long as</em> a condition is true, use a while loop.</p>
        <pre><code>while not_hungry == False:
    eat_cookie()</code></pre>

        <h2>When to Stop</h2>
        <p>Infinite loops happen when the condition never becomes false. Ensure your loop has a way to end.</p>

        <hr>
        <div class="module-nav">
            <a href="/beginner/module-04.html">&larr; Previous</a>
            <a href="/learn/">Next Part: Learn &rarr;</a>
        </div>
    """
})

# --- Learn (Part III - X) ---
learn_intro = """
    <h1>Learn: Tools & Concepts</h1>
    <p class="intro">Moving from basic commands to structured thinking and machine learning.</p>

    <h2>Part III: Working with Groups of Data</h2>
    <ul>
        <li><a href="/learn/module-06.html">Module 6: Lists</a></li>
        <li><a href="/learn/module-07.html">Module 7: Dictionaries</a></li>
    </ul>

    <h2>Part IV: Organizing Your Thinking</h2>
    <ul>
        <li><a href="/learn/module-08.html">Module 8: Functions</a></li>
        <li><a href="/learn/module-09.html">Module 9: Saving and Loading Data</a></li>
    </ul>

    <h2>Part V: Introducing Data Thinking</h2>
    <ul>
        <li><a href="/learn/module-10.html">Module 10: Pandas (Gentle Intro)</a></li>
        <li><a href="/learn/module-11.html">Module 11: Cleaning Data</a></li>
    </ul>

    <h2>Part VI: Numerical Intuition</h2>
    <ul>
        <li><a href="/learn/module-12.html">Module 12: Thinking in Numbers</a></li>
        <li><a href="/learn/module-13.html">Module 13: NumPy Without Fear</a></li>
    </ul>

    <h2>Part VII: How Machines Learn</h2>
    <ul>
        <li><a href="/learn/module-14.html">Module 14: What ML Actually Is</a></li>
        <li><a href="/learn/module-15.html">Module 15: First Learning Algorithm</a></li>
    </ul>

    <h2>Part VIII: Using ML Tools Responsibly</h2>
    <ul>
        <li><a href="/learn/module-16.html">Module 16: Scikit-Learn</a></li>
    </ul>

    <h2>Part IX: Preparing for Modern AI</h2>
    <ul>
        <li><a href="/learn/module-17.html">Module 17: From Features to Representations</a></li>
        <li><a href="/learn/module-18.html">Module 18: Readiness for Deep Learning</a></li>
    </ul>

    <h2>Part X: Ethics & Limits</h2>
    <ul>
        <li><a href="/learn/module-19.html">Module 19: Where ML Goes Wrong</a></li>
    </ul>
"""
pages.append({'path': 'learn/index.html', 'title': 'Learn Modules', 'content': learn_intro})

# Modules 6-19
pages.append({
    'path': 'learn/module-06.html',
    'title': 'Module 6: Lists',
    'content': """
        <h1>Module 6: Lists</h1>

        <h2>Storing Multiple Values</h2>
        <p>A variable can hold one thing. A list can hold many things.</p>
        <pre><code>scores = [85, 90, 78, 92]</code></pre>

        <h2>Looping</h2>
        <p>Lists and loops are best friends. You can go through every item in a list.</p>

        <h2>Min, Max, Average Manually</h2>
        <p>Before using fancy functions, try to find the largest number in a list yourself using a loop. It helps you understand the logic.</p>

        <hr>
        <div class="module-nav">
            <a href="/beginner/module-05.html">&larr; Previous</a>
            <a href="/learn/module-07.html">Next: Module 7 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-07.html',
    'title': 'Module 7: Dictionaries',
    'content': """
        <h1>Module 7: Dictionaries</h1>

        <h2>Key–Value Pairs</h2>
        <p>Lists are ordered by numbers (index). Dictionaries are labeled by keys.</p>
        <pre><code>user = {"name": "Jules", "role": "AI"}</code></pre>

        <h2>Structured Records</h2>
        <p>This is perfect for representing a single "thing" with properties, like a row in a spreadsheet.</p>

        <h2>Lists of Dictionaries</h2>
        <p>A dataset is often just a list of dictionaries.</p>
        <pre><code>users = [
  {"name": "Alice", "score": 10},
  {"name": "Bob", "score": 8}
]</code></pre>

        <h2>Why Structure Matters</h2>
        <p>ML models need data to be organized consistently. Dictionaries provide that consistency.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-06.html">&larr; Previous</a>
            <a href="/learn/module-08.html">Next: Module 8 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-08.html',
    'title': 'Module 8: Functions',
    'content': """
        <h1>Module 8: Functions</h1>

        <h2>Inputs / Outputs</h2>
        <p>A function is a machine: data goes in (arguments), work happens, result comes out (return).</p>

        <h2>Reuse</h2>
        <p>Don't repeat yourself. If you write the same code twice, put it in a function.</p>

        <h2>Refactoring Fearlessly</h2>
        <p>Functions make code easier to change. You fix the logic in one place, and it updates everywhere.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-07.html">&larr; Previous</a>
            <a href="/learn/module-09.html">Next: Module 9 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-09.html',
    'title': 'Module 9: Saving and Loading Data',
    'content': """
        <h1>Module 9: Saving and Loading Data</h1>

        <h2>Files</h2>
        <p>Variables die when the program ends. Files live on your hard drive. We learn to read from and write to text files.</p>

        <h2>CSVs</h2>
        <p>Comma Separated Values. The standard format for simple data. It's just text, but structured.</p>

        <h2>Persistence</h2>
        <p>Saving the state of your program allows you to pause and resume work.</p>

        <h2>Intro to Datasets</h2>
        <p>Real ML starts with loading a file full of data.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-08.html">&larr; Previous</a>
            <a href="/learn/module-10.html">Next: Module 10 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-10.html',
    'title': 'Module 10: Pandas (Gentle Intro)',
    'content': """
        <h1>Module 10: Pandas (Gentle Intro)</h1>

        <h2>DataFrames</h2>
        <p>Think of a DataFrame as a programmable Excel sheet.</p>

        <h2>Viewing Data</h2>
        <p><code>df.head()</code> lets you peek at the first few rows. Always look at your data.</p>

        <h2>Columns</h2>
        <p>Selecting a column is like selecting a key in a dictionary, but for all rows at once.</p>

        <h2>Basic Stats</h2>
        <p><code>df.describe()</code> gives you the summary: count, mean, min, max. This is your first step in understanding a dataset.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-09.html">&larr; Previous</a>
            <a href="/learn/module-11.html">Next: Module 11 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-11.html',
    'title': 'Module 11: Cleaning Data',
    'content': """
        <h1>Module 11: Cleaning Data</h1>

        <h2>Missing Values</h2>
        <p>Real data is messy. There are holes. You must decide: fill them or throw the row away?</p>

        <h2>Filtering</h2>
        <p>Removing rows that are errors or irrelevant.</p>

        <h2>Sorting</h2>
        <p>Organizing data to find patterns.</p>

        <h2>Why Cleaning > Models</h2>
        <p>A simple model on clean data beats a complex model on dirty data every time. Garbage in, garbage out.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-10.html">&larr; Previous</a>
            <a href="/learn/module-12.html">Next: Module 12 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-12.html',
    'title': 'Module 12: Thinking in Numbers',
    'content': """
        <h1>Module 12: Thinking in Numbers</h1>

        <h2>Averages</h2>
        <p>The middle of the data. But which middle? Mean? Median?</p>

        <h2>Variance (Conceptual)</h2>
        <p>How spread out is the data? Are all points close to the average, or all over the place?</p>

        <h2>Patterns vs Noise</h2>
        <p>Is that spike a real trend, or just a random fluctuation?</p>

        <h2>Distributions</h2>
        <p>The shape of the data. Most things in nature follow a "bell curve" (Normal distribution).</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-11.html">&larr; Previous</a>
            <a href="/learn/module-13.html">Next: Module 13 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-13.html',
    'title': 'Module 13: NumPy Without Fear',
    'content': """
        <h1>Module 13: NumPy Without Fear</h1>

        <h2>Arrays vs Lists</h2>
        <p>Lists are flexible but slow. NumPy arrays are rigid but incredibly fast.</p>

        <h2>Vector Operations</h2>
        <p>Instead of looping to add numbers, you can add two arrays together in one go. <code>[1, 2] + [3, 4] = [4, 6]</code>.</p>

        <h2>Shapes</h2>
        <p>Understanding dimensions (rows, columns). 2D arrays are matrices.</p>

        <h2>Why ML Prefers Vectors</h2>
        <p>Machine learning is essentially math on giant lists of numbers. NumPy makes that math efficient.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-12.html">&larr; Previous</a>
            <a href="/learn/module-14.html">Next: Module 14 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-14.html',
    'title': 'Module 14: What ML Actually Is',
    'content': """
        <h1>Module 14: What ML Actually Is</h1>

        <h2>Models as Adjustable Formulas</h2>
        <p>A model is just a math formula with knobs (parameters). <code>y = mx + b</code> is a model. <code>m</code> and <code>b</code> are the knobs.</p>

        <h2>Training vs Predicting</h2>
        <p><strong>Training</strong> is twiddling the knobs until the formula matches your data.<br>
        <strong>Predicting</strong> is using the tuned formula on new data.</p>

        <h2>Error Reduction</h2>
        <p>Learning is simply the process of reducing the error between what the model predicts and what is true.</p>

        <h2>Data > Algorithms</h2>
        <p>Better data usually beats a fancier algorithm.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-13.html">&larr; Previous</a>
            <a href="/learn/module-15.html">Next: Module 15 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-15.html',
    'title': 'Module 15: First Learning Algorithm',
    'content': """
        <h1>Module 15: First Learning Algorithm (From Scratch)</h1>

        <h2>Linear Relationships</h2>
        <p>Drawing a straight line through data points.</p>

        <h2>Loss</h2>
        <p>A score of how bad your model is. If the line is far from the dots, Loss is high.</p>

        <h2>Gradient Descent (Conceptual)</h2>
        <p>Imagine standing on a hill blindfolded. To get to the bottom, you feel the slope and step downhill. The computer does this to find the lowest Loss.</p>

        <h2>Overfitting Visually</h2>
        <p>If you connect the dots exactly, the line looks crazy and won't work for new dots. A simpler line is often better.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-14.html">&larr; Previous</a>
            <a href="/learn/module-16.html">Next: Module 16 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-16.html',
    'title': 'Module 16: Scikit-Learn',
    'content': """
        <h1>Module 16: Scikit-Learn</h1>

        <h2>Train/Test Split</h2>
        <p>Hide some data from the model during training. Test the model on this hidden data to see if it really learned.</p>

        <h2>Fit / Predict</h2>
        <p>The universal pattern in Scikit-Learn:<br>
        1. <code>model.fit(training_data)</code> (Learn)<br>
        2. <code>model.predict(new_data)</code> (Use)</p>

        <h2>Metrics</h2>
        <p>Accuracy is just one number. Precision, Recall, and others tell a fuller story.</p>

        <h2>Compare Models</h2>
        <p>Try different algorithms. See which one works best for your specific problem.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-15.html">&larr; Previous</a>
            <a href="/learn/module-17.html">Next: Module 17 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-17.html',
    'title': 'Module 17: From Features to Representations',
    'content': """
        <h1>Module 17: From Features to Representations</h1>

        <h2>Features</h2>
        <p>Features are the inputs to your model (columns in your spreadsheet). Choosing good features is an art.</p>

        <h2>Embeddings</h2>
        <p>Turning complex things like words or images into lists of numbers (vectors) that capture their meaning.</p>

        <h2>Distance as Meaning</h2>
        <p>In this vector space, words with similar meanings are mathematically close to each other.</p>

        <h2>High-level Neural Nets</h2>
        <p>Neural networks are just layers of these transformations, learning their own features.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-16.html">&larr; Previous</a>
            <a href="/learn/module-18.html">Next: Module 18 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-18.html',
    'title': 'Module 18: Readiness for Deep Learning & SLMs',
    'content': """
        <h1>Module 18: Readiness for Deep Learning & SLMs</h1>

        <h2>What Deep Learning Adds</h2>
        <p>It allows the computer to learn features from raw data (pixels, audio), rather than humans creating them.</p>

        <h2>When Small Models Suffice</h2>
        <p>You don't always need a massive brain. Often a simple regression is faster, cheaper, and more explainable.</p>

        <h2>Why Scale Matters</h2>
        <p>Sometimes, more data and bigger models unlock new capabilities.</p>

        <h2>PyTorch Overview</h2>
        <p>The standard tool for building deep learning models today. It's like NumPy, but with superpowers (gradients).</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-17.html">&larr; Previous</a>
            <a href="/learn/module-19.html">Next: Module 19 &rarr;</a>
        </div>
    """
})

pages.append({
    'path': 'learn/module-19.html',
    'title': 'Module 19: Where ML Goes Wrong',
    'content': """
        <h1>Module 19: Where ML Goes Wrong</h1>

        <h2>Bias</h2>
        <p>If your training data is biased, your model will be biased. Machines amplify human prejudices.</p>

        <h2>Misuse</h2>
        <p>Just because you <em>can</em> build it, doesn't mean you <em>should</em>.</p>

        <h2>Overconfidence</h2>
        <p>Models can be confidently wrong. Never trust a prediction blindly.</p>

        <h2>When Not to Automate</h2>
        <p>Some decisions require human empathy and judgment.</p>

        <hr>
        <div class="module-nav">
            <a href="/learn/module-18.html">&larr; Previous</a>
            <a href="/build/">Next Part: Build &rarr;</a>
        </div>
    """
})

# --- Build (Capstone) ---
pages.append({
    'path': 'build/index.html',
    'title': 'Build: The Capstone',
    'content': """
        <h1>Build: The Capstone</h1>
        <p class="intro">Putting it all together.</p>

        <p>You have learned the concepts. Now it is time to build something real.</p>

        <h2>Final Capstone: Build and Explain a Simple ML System</h2>
        <p>The goal is not to build the most advanced model, but to build a <strong>complete</strong> one and explain how it works.</p>

        <br>
        <a href="/build/capstone.html" class="cta-button">Start Capstone</a>
    """
})

pages.append({
    'path': 'build/capstone.html',
    'title': 'Capstone Project',
    'content': """
        <h1>Capstone Project</h1>

        <h2>The Task</h2>
        <p>Build and explain a simple machine learning system from scratch.</p>

        <h2>Steps</h2>
        <ol>
            <li><strong>Load Data</strong>: Find a simple CSV dataset (e.g., housing prices, flower measurements).</li>
            <li><strong>Clean It</strong>: Handle missing values, fix errors.</li>
            <li><strong>Explore It</strong>: Create charts, calculate averages. Understand what you have.</li>
            <li><strong>Train a Model</strong>: Use Scikit-Learn to fit a model (Linear Regression, Decision Tree).</li>
            <li><strong>Evaluate It</strong>: Check how well it performs on test data.</li>
            <li><strong>Explain Results</strong>: Write a plain-language summary of what your model learned.</li>
        </ol>

        <h2>Core Rule</h2>
        <blockquote>If you can explain it, you understand it.</blockquote>

        <hr>
        <div class="module-nav">
            <a href="/build/">&larr; Back to Build</a>
            <a href="/reflections/">Next: Reflections &rarr;</a>
        </div>
    """
})

# --- Reflections ---
pages.append({
    'path': 'reflections/index.html',
    'title': 'Reflections',
    'content': """
        <h1>Reflections</h1>
        <p class="intro">The end of the beginning.</p>

        <h2>End State</h2>
        <p>If you have followed this path, you now:</p>
        <ul>
            <li>Think step-by-step without fear.</li>
            <li>Understand data before models.</li>
            <li>See ML as logical, not mystical.</li>
            <li>Are genuinely ready for deep learning.</li>
        </ul>

        <h2>What's Next?</h2>
        <p>The field is vast. Keep building. Keep learning. But always remember to stay grounded in the fundamentals.</p>

        <p>Thank you for walking this path.</p>
    """
})

# --- Manifesto ---
pages.append({
    'path': 'manifesto.html',
    'title': 'Manifesto',
    'content': """
        <h1>Manifesto</h1>
        <p class="intro">Why Working Intelligence exists.</p>

        <p>We believe that understanding Artificial Intelligence should not be reserved for the elite or the mathematically gifted.</p>
        <p>We believe in slowness. In a world of hype and speed, true understanding requires patience.</p>
        <p>We believe in honesty. We strip away the magic to show the machinery underneath.</p>
        <p>We believe that code is a tool for thinking.</p>
    """
})

# --- About ---
pages.append({
    'path': 'about.html',
    'title': 'About',
    'content': """
        <h1>About Working Intelligence</h1>

        <p>This is a clean, static, beginner-friendly learning website that teaches Python, Machine Learning, and Applied AI slowly, honestly, and practically.</p>

        <h2>Our Philosophy</h2>
        <ul>
            <li>Learning happens through small working programs.</li>
            <li>Mistakes are expected and embraced.</li>
            <li>Concepts come before libraries.</li>
            <li>Code must run locally.</li>
            <li>Every abstraction must be grounded.</li>
        </ul>

        <p>Built with purpose.</p>
    """
})

# Generate files
for page in pages:
    full_html = get_template(page['title'], page['content'], page['path'])
    write_file(page['path'], full_html)

print("All files generated with relative paths.")
