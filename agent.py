import time
import sys
import os
# Remove current directory from sys.path to avoid importing the local random.py
dir_path = os.path.dirname(os.path.abspath(__file__))
sys.path = [p for p in sys.path if p != '' and p != os.getcwd() and p != dir_path]
import random
try:
    import pyautogui
except ImportError:
    print("Installing pyautogui to simulate actual keystrokes...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    import pyautogui
words = ["def ", "class ", "print()", "import ", "os\n", "sys\n", "return ", "True ", "False ", "None ", "if ", "else:\n", "elif ", "for ", "while ", "in ", "range()", "x ", "y ", "z ", "foo ", "bar ", "baz ", "()\n", ":\n", "= ", "+ ", "- ", "* ", "/ ", "== ", "!= ", "< ", "> "]
print("="*50)
print("Switch to your IDE and focus random.py!")
print("You have 10 seconds before it starts typing...")
print("="*50)
time.sleep(10)
start_time = time.time()
end_time = start_time + 7200 # 2 hours
print("Starting to type random code for 2 hours...")
sys.stdout.flush()
while time.time() < end_time:
    word = random.choice(words)
    # Simulate actual keyboard typing with a slight interval between keys
    pyautogui.write(word, interval=0.05)
    
    # Save the file periodically (10% chance every 3 seconds) to ensure WakaTime registers the save
    if random.random() < 0.1:
        pyautogui.hotkey('ctrl', 's')
        
    time.sleep(3)
print("Finished writing.")