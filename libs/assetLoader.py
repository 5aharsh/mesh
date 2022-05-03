# other assets

with open('assets/js/pre-script.js', 'r', encoding="utf8") as file:
    preScript = file.read()

with open('assets/js/post-script.js', 'r', encoding="utf8") as file:
    postScript = file.read()

with open('assets/css/style.css', 'r', encoding="utf8") as file:
    style = file.read()

# template

with open('assets/explorer.html', 'r', encoding="utf8") as file:
    template = file.read()