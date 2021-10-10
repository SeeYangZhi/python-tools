import glob, os

DIR = "/media/"

# Change working directory to DIR
os.chdir(DIR)

for file in glob.glob("*.mp4"):
    # Replace certain string in filename to desired string
    os.rename(file, file.replace(".", ""))

for file in glob.glob("*.mp4"):
    print(file)
