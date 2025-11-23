import os
import re
import sys

def extract_replain_text(html_content):
    """
    Extract the Replain text from the HTML content.
    Starts from <h2> title and ends before </span><hr>
    Removes <br> and </br> tags.
    """
    # Find the start: after <h2 ...> and before </span>
    # But to simplify, find the span content
    span_start = html_content.find('<span class="Fynelipa">')
    if span_start == -1:
        return ""
    
    span_end = html_content.find('</span>', span_start)
    if span_end == -1:
        return ""
    
    # Extract the content inside span
    span_content = html_content[span_start + len('<span class="Fynelipa">'):span_end].strip()
    
    # Remove <br> and </br> tags, and replace with newline for readability
    # But per request, remove them (so no newline, just concatenate)
    span_content = re.sub(r'<br\s*/?>|</br>', '', span_content)
    
    # Also remove any other HTML tags if present, but assuming mostly text and br
    # Use regex to strip all tags
    span_content = re.sub(r'<[^>]+>', '', span_content)
    
    return span_content.strip()

def process_directory(directory_path):
    """
    Process all HTML files in the directory.
    """
    if not os.path.exists(directory_path):
        print(f"Directory {directory_path} does not exist.")
        return
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.html'):
            html_path = os.path.join(directory_path, filename)
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            replain_text = extract_replain_text(html_content)
            
            if replain_text:
                # Output filename: "len_alen_" + filename.replace('.html', '.txt')
                base_name = filename.replace('.html', '.txt')
                txt_filename = f"len_alen_{base_name}"
                txt_path = os.path.join(directory_path, txt_filename)
                
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(replain_text)
                
                print(f"Extracted to {txt_filename}")
            else:
                print(f"No Replain text found in {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    process_directory(directory_path)