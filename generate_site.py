import os
import re

# --- Simple Markdown Parser ---
# Since we can't depend on external libraries, we'll write a simple parser
# sufficient for our needs (headers, paragraphs, lists, code blocks, links).

def parse_markdown(text):
    html = ""
    lines = text.split('\n')
    in_code_block = False
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Code Blocks
        if stripped.startswith('```'):
            if in_code_block:
                html += "</pre></code>\n"
                in_code_block = False
            else:
                lang = stripped[3:].strip()
                html += f'<pre><code class="language-{lang}">'
                in_code_block = True
            continue

        if in_code_block:
            # Escape HTML characters in code
            line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            html += line + "\n"
            continue

        # Headers
        if stripped.startswith('# '):
            html += f"<h1>{stripped[2:]}</h1>\n"
            continue
        if stripped.startswith('## '):
            html += f"<h2>{stripped[3:]}</h2>\n"
            continue
        if stripped.startswith('### '):
            html += f"<h3>{stripped[4:]}</h3>\n"
            continue

        # Lists (Unordered)
        if stripped.startswith('* ') or stripped.startswith('- '):
            if not in_list:
                html += "<ul>\n"
                in_list = True
            content = stripped[2:]
            # Handle bold/links inside list items
            content = parse_inline(content)
            html += f"<li>{content}</li>\n"
            continue

        # Lists (Ordered) - Simple check for "1. "
        # Note: robust ordered list parsing is harder, but let's handle "1. "
        if re.match(r'^\d+\.\s', stripped):
             # For simplicity in this custom parser, treating ordered lists as unordered for now
             # or just simple paragraphs if we don't want to track state complexly.
             # Let's try to handle them if they are sequential?
             # Actually, mixing ul and ol in a simple state machine is tricky without lookahead.
             # Let's just output them as list items in a ul for now, or start a new list type if needed.
             # Simpler: Just make them list items.
             if not in_list:
                 html += "<ul>\n"
                 in_list = True
             content = re.sub(r'^\d+\.\s', '', stripped)
             content = parse_inline(content)
             html += f"<li>{content}</li>\n"
             continue

        if in_list:
            if not stripped:
                # Empty line closes list? Not necessarily in MD, but let's say yes for simplicity
                html += "</ul>\n"
                in_list = False
            elif not (stripped.startswith('* ') or stripped.startswith('- ') or re.match(r'^\d+\.\s', stripped)):
                 html += "</ul>\n"
                 in_list = False

        # Empty lines
        if not stripped:
            continue

        # Paragraphs
        # If not a header, list, or code, it's a paragraph.
        # But we need to handle inline styles.
        content = parse_inline(stripped)
        html += f"<p>{content}</p>\n"

    if in_list:
        html += "</ul>\n"

    return html

def parse_inline(text):
    # Bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic *text*
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Code `text`
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    # Links [text](url)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    return text

# --- Generator Logic ---

def write_file(path, content):
    if os.path.dirname(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    print(f"Created {path}")

def get_relative_path(current_path, target_path):
    if target_path.startswith('http'):
        return target_path
    target_clean = target_path.lstrip('/')
    if target_path == '/':
        target_clean = '.'
    current_dir = os.path.dirname(current_path)
    if current_dir == '':
        current_dir = '.'
    rel = os.path.relpath(target_clean, current_dir)
    if target_path.endswith('/') and target_path != '/':
        rel = os.path.join(rel, 'index.html')
    elif target_path == '/':
         rel = os.path.join(rel, 'index.html')
    return rel

def get_template(title, content, current_page_path):
    nav_items = [
        ('/', 'Home'),
        ('/path/', 'The Path'),
        ('/setup.html', 'Setup'),
        ('/beginner/', 'Beginner'),
        ('/learn/', 'Learn'),
        ('/build/', 'Build'),
        ('/reflections/', 'Reflections'),
        ('/about.html', 'About'),
    ]

    nav_html = ""
    for link_target, text in nav_items:
        rel_link = get_relative_path(current_page_path, link_target)
        is_active = False
        if link_target == '/':
            if current_page_path == 'index.html':
                is_active = True
        else:
            if current_page_path.startswith(link_target.lstrip('/')):
                is_active = True
        active_class = ' class="active"' if is_active else ''
        nav_html += f'<a href="{rel_link}"{active_class}>{text}</a>\n'

    css_rel = get_relative_path(current_page_path, '/style.css')

    # Fix content links (basic regex replacement for absolute paths)
    def replace_link(match):
        full_match = match.group(0)
        url = match.group(1)
        if url.startswith('/'):
            return f'href="{get_relative_path(current_page_path, url)}"'
        return full_match

    processed_content = re.sub(r'href="(/[^"]*)"', replace_link, content)

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

# --- Main Build Process ---

# 1. Define Standard Pages (Hardcoded for now if not in markdown)
# We will check if a markdown file exists in `content/`, if so use it.
# Otherwise fall back to the old hardcoded strings (or ideally, move ALL to markdown).

# Let's map paths to source files.
# If key is in content_map, we read the MD. If not, we use the string.

content_map = {
    'setup.html': 'content/setup.md',
    'beginner/module-01.html': 'content/beginner/module-01.md',
    'beginner/module-02.html': 'content/beginner/module-02.md',
}

# Define the full list of pages we expect to generate
pages_meta = [
    {'path': 'index.html', 'title': 'Working Intelligence', 'type': 'hardcoded'}, # Keep home hardcoded for custom layout
    {'path': 'path/index.html', 'title': 'The Path', 'type': 'hardcoded'},
    {'path': 'setup.html', 'title': 'Setting Up Your Environment', 'type': 'markdown'},

    # Beginner
    {'path': 'beginner/index.html', 'title': 'Beginner Foundations', 'type': 'hardcoded'},
    {'path': 'beginner/module-01.html', 'title': 'Module 1', 'type': 'markdown'},
    {'path': 'beginner/module-02.html', 'title': 'Module 2', 'type': 'markdown'},
    {'path': 'beginner/module-03.html', 'title': 'Module 3', 'type': 'hardcoded'}, # Not converted yet
    {'path': 'beginner/module-04.html', 'title': 'Module 4', 'type': 'hardcoded'},
    {'path': 'beginner/module-05.html', 'title': 'Module 5', 'type': 'hardcoded'},

    # Learn
    {'path': 'learn/index.html', 'title': 'Learn Modules', 'type': 'hardcoded'},
    # ... mapped modules 6-19 would go here, currently hardcoded in the loop below

    # Build
    {'path': 'build/index.html', 'title': 'Build', 'type': 'hardcoded'},
    {'path': 'build/capstone.html', 'title': 'Capstone', 'type': 'hardcoded'},

    # Other
    {'path': 'reflections/index.html', 'title': 'Reflections', 'type': 'hardcoded'},
    {'path': 'manifesto.html', 'title': 'Manifesto', 'type': 'hardcoded'},
    {'path': 'about.html', 'title': 'About', 'type': 'hardcoded'},
]

# Old hardcoded content store (simplified for brevity where replaced)
hardcoded_content = {
    'index.html': """
        <h1>Working Intelligence</h1>
        <p class="intro">Learning to Teach Machines — Slowly, Clearly, Honestly.</p>
        <p>A gentle path from Python to Machine Learning.<br>No hype. No shortcuts. No intimidation.</p>
        <br>
        <a href="/path/" class="cta-button">Start the Path</a>
    """,
    'path/index.html': """
        <h1>The Path</h1>
        <p class="intro">Understanding matters more than speed.</p>
        <h2>What is this learning journey?</h2>
        <p>This is a curriculum designed for absolute beginners who want to become real ML builders.</p>
        <br>
        <a href="/setup.html" class="cta-button">Get Set Up First</a>
        <a href="/beginner/" class="cta-button" style="margin-left: 1rem; background: #fff; color: #000; border: 1px solid #ccc;">Then Begin Part I</a>
    """,
    'beginner/index.html': """
        <h1>Beginner: Foundations</h1>
        <p class="intro">Learning to speak the language of the machine.</p>
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
    """,
    # ... (I need to preserve the old modules 3-19 content here or just generate them via a loop if I want to keep them 'thin' for now)
}

# Let's reconstitute the 'thin' modules (3-19) so we don't lose them while we only upgraded 1 & 2.
# I will use a helper to just inject the text I had before.

thin_modules = {
    'beginner/module-03.html': ('Module 3: Variables and Simple Data', """
        <h1>Module 3: Variables and Simple Data</h1>
        <h2>Numbers and Text</h2>
        <p>Computers work with data. Two basic types are numbers (like <code>42</code>) and text (strings, like <code>"Hello"</code>).</p>
        <h2>Naming (Variables)</h2>
        <p>A variable is a label for a value. It lets us store data to use later.</p>
        <pre><code>user_name = "Jules"</code></pre>
        <h2>Why Types Matter</h2>
        <p>You can add two numbers, but you cannot add a number to a string. Python needs to know the type.</p>
        <hr>
        <div class="module-nav"><a href="/beginner/module-02.html">&larr; Previous</a> <a href="/beginner/module-04.html">Next &rarr;</a></div>
    """),
    'beginner/module-04.html': ('Module 4: Asking Questions', """
        <h1>Module 4: Asking Questions</h1>
        <h2>Input</h2>
        <p>We can ask the user for input using <code>input()</code>.</p>
        <h2>If / Else</h2>
        <p>We can make decisions based on data.</p>
        <pre><code>if age >= 18: print("Adult")</code></pre>
        <hr>
        <div class="module-nav"><a href="/beginner/module-03.html">&larr; Previous</a> <a href="/beginner/module-05.html">Next &rarr;</a></div>
    """),
    'beginner/module-05.html': ('Module 5: Repeating Work', """
        <h1>Module 5: Repeating Work</h1>
        <h2>Loops</h2>
        <p>Use <code>for</code> loops to repeat a specific number of times.</p>
        <p>Use <code>while</code> loops to repeat as long as a condition is true.</p>
        <hr>
        <div class="module-nav"><a href="/beginner/module-04.html">&larr; Previous</a> <a href="/learn/">Next Part &rarr;</a></div>
    """),
    'learn/index.html': ('Learn Modules', """
        <h1>Learn: Tools & Concepts</h1>
        <p class="intro">Moving from basic commands to structured thinking and machine learning.</p>
        <ul>
            <li><a href="/learn/module-06.html">Module 6: Lists</a></li>
            <li><a href="/learn/module-07.html">Module 7: Dictionaries</a></li>
            <li><a href="/learn/module-08.html">Module 8: Functions</a></li>
            <li><a href="/learn/module-09.html">Module 9: Saving and Loading Data</a></li>
            <li><a href="/learn/module-10.html">Module 10: Pandas</a></li>
            <li>...and more.</li>
        </ul>
    """),
    'build/index.html': ('Build', """
        <h1>Build: The Capstone</h1>
        <p>You have learned the concepts. Now it is time to build something real.</p>
        <a href="/build/capstone.html" class="cta-button">Start Capstone</a>
    """),
    'build/capstone.html': ('Capstone', """
        <h1>Capstone Project</h1>
        <p>Build and explain a simple machine learning system from scratch.</p>
        <hr>
        <div class="module-nav"><a href="/build/">&larr; Back</a> <a href="/reflections/">Next &rarr;</a></div>
    """),
    'reflections/index.html': ('Reflections', """
        <h1>Reflections</h1>
        <p>If you have followed this path, you now think step-by-step without fear.</p>
    """),
    'manifesto.html': ('Manifesto', """
        <h1>Manifesto</h1>
        <p>We believe in slowness. In a world of hype and speed, true understanding requires patience.</p>
    """),
    'about.html': ('About', """
        <h1>About Working Intelligence</h1>
        <p>This is a clean, static, beginner-friendly learning website.</p>
    """),
}

# --- Execution ---

# 1. Generate Hardcoded/Legacy Pages
for path, (title, content) in thin_modules.items():
    full_html = get_template(title, content, path)
    write_file(path, full_html)

# 2. Generate Explicitly Defined Pages (Mixed Type)
for page in pages_meta:
    path = page['path']
    # Skip if already handled by thin_modules (overlap check)
    if path in thin_modules:
        continue

    html_content = ""

    if page['type'] == 'hardcoded':
        if path in hardcoded_content:
            html_content = hardcoded_content[path]
        else:
            html_content = f"<h1>{page['title']}</h1><p>Content coming soon.</p>"

    elif page['type'] == 'markdown':
        src = content_map.get(path)
        if src and os.path.exists(src):
            with open(src, 'r') as f:
                md_text = f.read()
            html_content = parse_markdown(md_text)

            # Add simple navigation footer for modules
            if 'module-' in path:
                # Basic nav logic (could be improved)
                html_content += '<hr><div class="module-nav"><a href="/beginner/">Back to Index</a></div>'
            if 'setup' in path:
                html_content += '<hr><div class="module-nav"><a href="/path/">Back to Path</a></div>'

        else:
            html_content = "<h1>Error</h1><p>Markdown source not found.</p>"

    full_html = get_template(page['title'], html_content, path)
    write_file(path, full_html)

print("Site generation complete.")
