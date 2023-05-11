import os

def remove_first_line(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        file.writelines(lines[2:])

def remove_first_line_in_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.md'):
            file_path = os.path.join(directory, filename)
            remove_first_line(file_path)

# Example usage
directory_path = '/Users/yangzhi/Library/Mobile Documents/iCloud~md~obsidian/Documents/Personal Journal/2023/04 April'
remove_first_line_in_directory(directory_path)
