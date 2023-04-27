list_style = """
width: 100%;
align-items: center;
text-align: center;
content-align: center;
justify-content: center;
""".replace('\n', '').replace('\r', '')
folder_base = '<li style="%s"><a href="/folder?folder={}{}/">{}/</a></li><br><br>' % list_style
files_base = '<li style="%s"><a href="/file?file={}{}">{}</a></li><br><br>' % list_style
