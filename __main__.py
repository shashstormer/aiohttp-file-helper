import os
from aiohttp import web

password = os.environ.get('file_manager_password')
replace_some_string_empty = os.environ.get('file_manager_replace_string', '')


async def index(_):
    """Render the file navigator interface"""
    # Render the template with the file list
    return web.Response(text=(await generate_page()), headers={'content-type': 'text/html'})


async def generate_page(path='./'):
    html = """
    <html>
        <head>
            <title>File Navigator</title>
        </head>
        <body>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" multiple><br><br>
                <button type="submit">Upload file(s)</button>
            </form>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" max_file_size="10000000" accept="*/*, !video/*, !application/*" webkitdirectory directory multiple value="upload dirs"><br><br>
                <button type="submit">Upload dir(s)</button>
            </form>
            <br><br>
            <form action="/delete" method="post">
                <input type="text" name="filename" placeholder="Enter filename"><br><br>
                <button type="submit">Delete</button>
            </form>
            <br><br>
            <ul>
                {}
            </ul>
        </body>
    </html>
    """
    # Get the list of files and folders in the current directory
    files = os.listdir(path)
    # Generate the HTML for the file list
    file_html = ''
    for f in files:
        if os.path.isdir(os.path.join(path, f)):
            file_html += f'<li><a href="/folder?folder={path + f}/">{f}/</a></li>'
        else:
            file_html += f'<li><a href="/file?file={path + f}">{f}</a></li>'
    return html.format(file_html)


async def upload(request):
    """Handle file uploads"""
    data = await request.post()
    files = data.getall('file')
    print(data)
    for _file in files:
        try:
            filename = _file.filename
            dir_file = os.path.dirname(filename)
            if not os.path.exists(dir_file):
                os.makedirs(dir_file)
            with open(filename, 'wb') as f:
                f.write(_file.file.read())
        except AttributeError:
            pass
    raise web.HTTPFound('/')


async def delete(request):
    """Handle file and folder deletions"""
    data = await request.post()
    filename = data.get('filename')
    if os.path.isfile(filename):
        os.remove(filename)
    elif os.path.isdir(filename):
        try:
            os.rmdir(filename)
        except OSError:
            for main, sub, files in os.walk(filename):
                for _file in files:
                    os.remove(os.path.join(main, _file))
                for folder in sub:
                    try:
                        os.rmdir(os.path.join(main, folder))
                    except OSError:
                        for _main, _sub, _files in os.walk(os.path.join(main, folder)):
                            for _file in _files:
                                os.remove(os.path.join(_main, _file))
                            for _folder in _sub:
                                os.rmdir(os.path.join(_main, _folder))
            try:
                os.remove(filename)
            except PermissionError:
                try:
                    os.remove(filename)
                except Exception as e:
                    print(e)
    # Redirect back to the file navigator interface
    raise web.HTTPFound('/')


async def file(request):
    try:
        return web.Response(text=open(request.query['file']).read()
                            .replace(replace_some_string_empty, '')
                            .replace(replace_some_string_empty.lower(), '')
                            .replace(replace_some_string_empty.replace('/', '\\'), '')
                            .replace(replace_some_string_empty.replace('/', '\\').lower(), '')
                            )
    except Exception as e:
        print(e)
        return web.FileResponse(request.query['file'])


async def folders(request):
    return web.Response(text=await generate_page(request.query['folder']), headers={'content-type': 'text/html'})


async def login(request):
    if request.query.get('password') == password or request.cookies.get('pass') == password:
        response = web.HTTPFound('/')
        response.set_cookie(
            'pass',
            value=password,
            max_age=None,
            path='/',
            secure=True,
            httponly=True,
            samesite='Strict',
        )
        return response
    return web.Response(
        text="<form method='GET' action='/login'><input type='text' name='password' id='password' 'placeholder='password' autocomplete='off' /></form>",
        headers={'content-type': 'text/html'})


app = web.Application(client_max_size=1000 * 1024 * 1024)
app.add_routes([
    web.get('/', index),
    web.post('/upload', upload),
    web.post('/delete', delete),
    web.get('/file', file),
    web.get('/folder', folders),
    web.get('/login', login)
])


@web.middleware
async def middlewares(request: web.Request, handler):
    if request.cookies.get('pass') == password or request.path == '/login':
        return await handler(request)
    else:
        return web.HTTPFound('/login', headers={'Content-Type': 'text/html'})


app.middlewares.append(middlewares)

if __name__ == '__main__':
    web.run_app(app, port=443)
