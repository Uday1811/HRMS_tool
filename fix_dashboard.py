
import os

file_path = r"c:\Users\sathi\Downloads\HRMS_tool-master\employee\templates\employee\employee_dashboard.html"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # The exact string to find. Note the newline and indentation.
    # We will regex split or just replace the specific substring.
    # The pattern implies a newline and some spaces.
    
    # Let's find the location of "Today ({% if shift_start %}"
    idx = content.find("Today ({% if shift_start %}")
    if idx == -1:
        print("Could not find the target string!")
        exit(1)
        
    print(f"Found at index {idx}")
    snippet = content[idx:idx+200]
    print(f"Snippet:\n{snippet!r}")
    
    # We want to remove the newline inside the if tag.
    # Look for "{% if" followed by whitespace/newlines and "shift_end"
    import re
    
    # Pattern: {% if\s+shift_end
    # We want to replace it with {% if shift_end
    
    new_content = re.sub(r"\{% if\s+shift_end", "{% if shift_end", content)
    
    if content == new_content:
        print("No changes made (regex match failed?)")
        # Try manual string replacement based on what we saw
        # The failing block is:
        # {% if
        #                             shift_end %}
        
        # Depending on line endings (\r\n vs \n)
        pass
    else:
        print("Regex replacement successful!")
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print("File written successfully.")
    
except Exception as e:
    print(f"Error: {e}")
