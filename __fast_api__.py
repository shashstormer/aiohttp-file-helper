import os
from typing import List
import uvicorn
from fastapi import FastAPI, Request, Response, UploadFile, Form
from fastapi.responses import RedirectResponse, FileResponse
from files import folder_base, files_base

password = os.environ.get('file_manager_password', 'password')
replace_some_string_empty = os.environ.get('file_manager_replace_string', '')
app = FastAPI()
html_mime = 'text/html'


@app.middleware('http')
@app.middleware('https')
async def middlewares(request: Request, handler):
    if (request.cookies.get('pass') == password) or (request.url.path == '/login'):
        response = await handler(request)
        return response
    else:
        response = RedirectResponse('/login', status_code=303)
        return response


@app.get('/')
@app.post('/')
async def index(_: Request):
    """Render the file navigator interface"""
    return Response(content=(await generate_page(path='./')), headers={'content-type': html_mime},
                    media_type=html_mime)


async def generate_page(path='./'):
    html = open('files.html').read()
    files = os.listdir(path)
    file_html = ''
    not_add = ['.git', '.idea']
    for f in files:
        if f in not_add:
            continue
        if os.path.isdir(os.path.join(path, f)):
            file_html += folder_base.format(path, f, f)
        else:
            file_html += files_base.format(path, f, f)
    return html.format(file_html).replace('Â', '')


@app.post('/upload')
async def upload(files: List[UploadFile]):
    """Handle file uploads"""
    for _file in files:
        try:
            filename = _file.filename
            dir_file = os.path.dirname(filename)
            if dir_file and not os.path.exists(dir_file):
                os.makedirs(dir_file)
            with open(filename, 'wb') as f:
                f.write(_file.file.read())
        except AttributeError:
            pass
    return RedirectResponse('/', status_code=303)


@app.post('/delete')
async def delete(filename: str = Form()):
    """Handle file and folder deletions"""
    print('delete :', filename)
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
                os.remove(filename.strip('/'))
            except PermissionError:
                try:
                    os.remove(filename.strip('/'))
                except Exception as e:
                    print(e)
    return RedirectResponse('/', status_code=303)


@app.get('/file')
async def file(request: Request):
    try:
        filename = request.query_params['file']
        content = (open(filename).read()
                   .replace(replace_some_string_empty, '')
                   .replace(replace_some_string_empty.lower(), '')
                   .replace(replace_some_string_empty.replace('/', '\\'), '')
                   .replace(replace_some_string_empty.replace('/', '\\').lower(), ''))
        download_mode = ['exe', 'pyc', 'msi', 'lib', 'dll']
        extension = content.split('.')[-1]
        filename = filename.split('/')[-1]
        print('end : "', extension, '"', sep='')
        if extension in download_mode:
            resp = Response(content=content, headers={
                "Content-Disposition": f'attachment; filename="{filename}"'})
        else:
            resp = Response(content=content)
        return resp
    except Exception as e:
        print(e)
        resp = FileResponse(request.query_params['file'],
                            headers={
                                "Content-Disposition": f'attachment; filename="{request.query_params["file"].split("/")[-1]}"'})
        regular = ['png', 'jpg', 'jpeg', 'mp4', 'mp3']
        if request.query_params['file'].split('.')[-1] in regular:
            resp = FileResponse(request.query_params['file'])
        return resp


@app.get('/folder')
async def folders(request: Request):
    return Response(content=await generate_page(request.query_params['folder']), headers={'content-type': 'text/html'})


@app.get('/login')
async def login(request: Request):
    if request.query_params.get('password') == password or request.cookies.get('pass') == password:
        response = RedirectResponse('/', status_code=303)
        response.set_cookie(
            key='pass',
            value=password,
            max_age=600,
            path='/',
            secure=True,
            httponly=True,
            samesite='strict', )
        return response
    return Response(
        content="<form method='GET' action='/login'><input type='text' name='password' id='password' 'placeholder='password' autocomplete='off' /></form>",
        headers={'content-type': html_mime})


app.add_api_route("/", index, methods=['GET', 'POST'])
app.add_api_route("/upload", upload, methods=['POST'])
app.add_api_route("/delete", delete, methods=['POST'])
app.add_api_route("/file", file, methods=['GET'])
app.add_api_route("/folder", folders, methods=['GET'])
app.add_api_route("/login", login, methods=['GET'])

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5080)
