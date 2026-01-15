import sys
import re

def validate():
    if len(sys.argv) ==  1:
        print("Error: No input provided")
        sys.exit(1)

    filename = sys.argv[1]

    if not filename.endswith(".fold"): 
        print("Error: Invalid file type")
        sys.exit(1)

    try:
        with open(filename, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Cannot read file (permission denied)")
        sys.exit(1)

    pattern = r'"file_classes":\s*\[\s*"([^"]+)"'
    
    if not re.search(pattern, content).group(1) == "singleModel":
        print("Error: Unable to process non-singleModel file_classes")
        sys.exit(1)
