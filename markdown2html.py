#!/usr/bin/python3
"""
Script that converts Markdown to HTML.
Usage: ./markdown2html.py README.md README.html
"""
import sys
import os
import re
import hashlib


def convert_heading(line):
    """Convert markdown heading to HTML heading."""
    level = len(line.split()[0])  # Count the number of #
    text = line.lstrip('#').strip()
    return f"<h{level}>{text}</h{level}>"


def convert_unordered_list(lines):
    """Convert markdown unordered list to HTML list."""
    items = [line.lstrip('- ').strip() for line in lines]
    html_items = [f"<li>{process_inline_markup(item)}</li>" for item in items]
    return "<ul>\n" + "\n".join(html_items) + "\n</ul>"


def convert_ordered_list(lines):
    """Convert markdown ordered list to HTML ordered list."""
    items = [line.lstrip('* ').strip() for line in lines]
    html_items = [f"<li>{process_inline_markup(item)}</li>" for item in items]
    return "<ol>\n" + "\n".join(html_items) + "\n</ol>"


def convert_paragraph(lines):
    """Convert markdown paragraph to HTML paragraph."""
    processed_lines = []
    for i, line in enumerate(lines):
        line = process_inline_markup(line)
        if i < len(lines) - 1 and lines[i + 1]:
            line += "<br/>"
        processed_lines.append(line)
    return "<p>\n" + "\n".join(processed_lines) + "\n</p>"


def process_inline_markup(text):
    """Process inline markdown markup (bold, emphasis, MD5, remove c)."""
    # Convert bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    # Convert emphasis
    text = re.sub(r'__([^_]+)__', r'<em>\1</em>', text)
    # Convert MD5
    md5_matches = re.findall(r'\[\[(.*?)\]\]', text)
    for match in md5_matches:
        md5_hash = hashlib.md5(match.encode()).hexdigest()
        text = text.replace(f"[[{match}]]", md5_hash)
    # Remove 'c' characters
    c_matches = re.findall(r'\(\((.*?)\)\)', text)
    for match in c_matches:
        no_c = re.sub(r'[cC]', '', match)
        text = text.replace(f"(({match}))", no_c)
    return text


def main():
    """Main function to convert markdown to HTML."""
    # Check arguments
    if len(sys.argv) != 3:
        print("Usage: ./markdown2html.py README.md README.html",
              file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

    # Read input file
    with open(input_file, 'r') as f:
        lines = f.readlines()

    html_lines = []
    current_block = []
    current_type = None

    # Process lines
    for line in lines:
        line = line.rstrip()

        # Determine line type
        if line.startswith('#'):
            if current_block:
                if current_type == 'ul':
                    html_lines.append(convert_unordered_list(current_block))
                elif current_type == 'ol':
                    html_lines.append(convert_ordered_list(current_block))
                elif current_type == 'p':
                    html_lines.append(convert_paragraph(current_block))
                current_block = []
            html_lines.append(convert_heading(line))
        elif line.startswith('- '):
            if current_type != 'ul' and current_block:
                if current_type == 'p':
                    html_lines.append(convert_paragraph(current_block))
                elif current_type == 'ol':
                    html_lines.append(convert_ordered_list(current_block))
                current_block = []
            current_type = 'ul'
            current_block.append(line)
        elif line.startswith('* '):
            if current_type != 'ol' and current_block:
                if current_type == 'p':
                    html_lines.append(convert_paragraph(current_block))
                elif current_type == 'ul':
                    html_lines.append(convert_unordered_list(current_block))
                current_block = []
            current_type = 'ol'
            current_block.append(line)
        elif line:
            if current_type != 'p' and current_block:
                if current_type == 'ul':
                    html_lines.append(convert_unordered_list(current_block))
                elif current_type == 'ol':
                    html_lines.append(convert_ordered_list(current_block))
                current_block = []
            current_type = 'p'
            current_block.append(line)
        elif current_block:
            if current_type == 'ul':
                html_lines.append(convert_unordered_list(current_block))
            elif current_type == 'ol':
                html_lines.append(convert_ordered_list(current_block))
            elif current_type == 'p':
                html_lines.append(convert_paragraph(current_block))
            current_block = []
            current_type = None

    # Handle last block if exists
    if current_block:
        if current_type == 'ul':
            html_lines.append(convert_unordered_list(current_block))
        elif current_type == 'ol':
            html_lines.append(convert_ordered_list(current_block))
        elif current_type == 'p':
            html_lines.append(convert_paragraph(current_block))

    # Write output file
    with open(output_file, 'w') as f:
        f.write('\n'.join(html_lines))

    sys.exit(0)


if __name__ == "__main__":
    main()
