# -*- coding: utf-8 -*-
import os
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Parent folder containing all scraped data
scraped_parent_folder = "D:\\Cassworld\\JARVIS AI\\AI_Assistant\\scraped_test"

# Memory list
odin_knowledge = []

# Function to assign tags based on folder name
def assign_tag(path):
    folder_name = os.path.basename(os.path.dirname(path)).lower()
    if "facebook" in folder_name:
        return "Omega"
    elif "website" in folder_name:
        return "Alpha"
    else:
        return "Eternium"

# Function to split text into chunks
def split_text(text, max_len=500):
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0
    for word in words:
        current_len += len(word) + 1
        current_chunk.append(word)
        if current_len >= max_len:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# Walk through all files
for root, dirs, files in os.walk(scraped_parent_folder):
    for file in files:
        if file.endswith(".txt"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                tag = assign_tag(path)
                chunks = split_text(text)
                for chunk in chunks:
                    odin_knowledge.append({
                        "source": path,
                        "text": chunk,
                        "tag": tag
                    })

# Print summary with color coding
tag_colors = {
    "Alpha": Fore.CYAN,
    "Omega": Fore.MAGENTA,
    "Eternium": Fore.YELLOW,
    "Materium": Fore.GREEN,
    "Lattice": Fore.BLUE
}

print(f"Loaded {len(odin_knowledge)} text chunks into ODIN memory\n")

# Example: print first 5 chunks with color
for i, item in enumerate(odin_knowledge[:5]):
    color = tag_colors.get(item["tag"], Fore.WHITE)
    print(f"{color}[{item['tag']}] {item['source']}\n{item['text'][:200]}...\n")
