# other assets

with open('assets/js/pre-script.js', 'r') as file:
    preScript = file.read()

with open('assets/js/post-script.js', 'r') as file:
    postScript = file.read()

with open('assets/css/style.css', 'r') as file:
    style = file.read()

# template

with open('assets/explorer.html', 'r') as file:
    template = file.read()