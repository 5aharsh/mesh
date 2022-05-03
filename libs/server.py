import os
import urllib.parse
import posixpath
import html
import sys
import io

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from .assetLoader import template, preScript, postScript, style

class FilerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, dir='/'):
        super().__init__(*args, directory=dir)

    def do_GET(self):
        """Overriding original GET handler to run apps
        and redirect while opening them
        """
        self.dirpath = self.translate_path(self.path)
        if os.path.isfile(self.dirpath):
            process = os.system('"{0}"'.format(self.dirpath))
            redirect_path = '/'.join(self.path.split('/')[:-1])+'/'
            self.send_response(HTTPStatus.MOVED_PERMANENTLY)
            self.send_header('Location', redirect_path)
            self.end_headers()
        else:
            f = self.send_head()
            if f:
                try:
                    self.copyfile(f, self.wfile)
                finally:
                    f.close()

    def translate_path(self, path):
        """Fix for Windows' stupid drives directory based system.
        Overriding original translate_path for SimpleHTTPServer 
        to serve multiple drives
        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        try:
            path = urllib.parse.unquote(path, errors='surrogatepass')
        except UnicodeDecodeError:
            path = urllib.parse.unquote(path)
        path = posixpath.normpath(path)
        path = path[1:]
        if trailing_slash:
            path += '/'
        return path
    
    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except OSError:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(self.path,
                                               errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        title = 'Filer - %s' % displaypath
        r.append('<ul class="directory-list">')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
                classname = "folder-item"
            else:
                classname = "file-item"
            if os.path.islink(fullname):
                displayname = name + "@"
                classname = "folder-item"
                # Note: a link to a directory displays with @ and links with /
            r.append('<a href="%s" title="%s"><li class="directory-item %s">%s</li></a>'
                        % (
                            urllib.parse.quote(linkname, errors='surrogatepass'),
                            html.escape(displayname, quote=False),
                            classname, 
                            html.escape(displayname, quote=False)
                        )
                    )
        r.append('</ul>')
        app = '\n'.join(r)
        page = template.format(style, preScript, app, postScript)
        encoded = page.encode(enc, 'surrogateescape')
        f = io.BytesIO()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f