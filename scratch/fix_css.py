import sys

file_path = "e:/Personal Projects/my_portfolio/static/css/styles.css"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_content = [
    ".project-image-main {\n",
    "    width: 100%;\n",
    "    height: 250px;\n",
    "    object-fit: cover;\n",
    "    border-radius: 12px;\n",
    "    transition: transform 0.3s ease;\n",
    "}\n",
    "\n",
    ".project-media {\n",
    "    width: 350px;\n",
    "    flex-shrink: 0;\n",
    "    display: flex;\n",
    "    flex-direction: column;\n",
    "    gap: 12px;\n",
    "    padding: 20px;\n",
    "}\n",
    "\n",
    ".project-images-secondary {\n",
    "    display: grid;\n",
    "    grid-template-columns: 1fr 1fr;\n",
    "    gap: 12px;\n",
    "}\n",
    "\n",
    ".project-image-small {\n",
    "    width: 100%;\n",
    "    height: 100px;\n",
    "    object-fit: cover;\n",
    "    border-radius: 8px;\n",
    "    transition: transform 0.3s ease;\n",
    "}\n",
    "\n",
    ".project-image-main:hover, .project-image-small:hover {\n",
    "    transform: scale(1.02);\n",
    "}\n",
    "\n",
    "@media (max-width: 768px) {\n",
    "    .project-card {\n",
    "        flex-direction: column !important;\n",
    "    }\n",
    "    .project-media {\n",
    "        width: 100%;\n",
    "        padding: 10px;\n",
    "    }\n",
    "}\n"
]

# Line 11963 is index 11962 (0-indexed)
# Line 11971 is index 11970 (0-indexed)
# So we replace lines[11962:11971]
lines[11962:11971] = new_content

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Replacement successful")
