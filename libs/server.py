import os
import urllib.parse
import posixpath
import html
import sys
import io

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from libs.assetLoader import template, preScript, postScript, style


class FilerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, dir='/'):
        super().__init__(*args, directory=dir)

    def do_GET(self):
        """Overriding original GET handler to run apps
        and redirect while opening them
        """
        self.dirpath = self.translate_path(self.path)
        if os.path.isfile(self.dirpath) or self.dirpath.startswith('search'):
            process = os.system('"{0}"'.format(self.dirpath))
            redirect_path = '/'.join(self.path.split('/')[:-1]) + '/'
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
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
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
        if path == '/':
            try:
                encoded = self.list_drives()
            except OSError:
                self.send_error(
                    HTTPStatus.NOT_FOUND,
                    "No permission to list directory")
                return None
        elif path.startswith('/search'):
            print(path)
            try:
                encoded = self.list_search(path)
            except OSError:
                self.send_error(
                    HTTPStatus.NOT_FOUND,
                    "No permission to list directory")
                return None
        else:
            try:
                encoded = self.list_dir(path)
            except OSError:
                self.send_error(
                    HTTPStatus.NOT_FOUND,
                    "No permission to list directory")
                return None
        f = io.BytesIO()
        enc = sys.getfilesystemencoding()
        f.write(encoded)
        f.seek(0)
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        return f

    def list_dir(self, path):
        list = os.listdir(path)
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(self.path,
                                               errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        r.append('<ul class="directory-list">')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                classname = "folder-item"
            else:
                classname = "file-item"
            if os.path.islink(fullname):
                classname = "folder-item"
                # Note: a link to a directory displays with @ and links with /
            r.append(
                '<a href="%s" title="%s" meta-name="%s" class="directory-link"><li class="directory-item %s">%s</li></a>'
                % (
                    urllib.parse.quote(linkname, errors='surrogatepass'),
                    html.escape(displayname, quote=False),
                    html.escape(displayname, quote=False),
                    classname,
                    html.escape(displayname, quote=False)
                )
                )
        r.append('</ul>')
        app = '\n'.join(r)
        navurl = "/"
        navitem = []
        navitem.append('<a href="%s" class="navpath">%s</a>'
                       % (
                           navurl,
                           "Home"
                       )
                       )
        for i in displaypath.split("/")[1:]:
            navurl += "%s/" % (i)
            navitem.append('<a href="%s" class="navpath">%s</a>'
                           % (
                               navurl,
                               i
                           )
                           )
        navhead = " &#x276D; ".join(navitem)
        title = " &#x276D; ".join(displaypath.split("/")[1:])
        page = template.format(
            style,
            preScript,
            app,
            postScript,
            navhead,
            title
        )
        encoded = page.encode(enc, 'surrogateescape')
        return encoded

    def list_drives(self):
        drives = [chr(x) + ":" for x in range(65, 91) if os.path.exists(chr(x) + ":")]
        r = []
        enc = sys.getfilesystemencoding()
        r.append('<ul class="directory-list">')
        for drive in drives:
            classname = "drive-item"
            linkname = drive + "/"
            # Note: a link to a directory displays with @ and links with /
            r.append(
                '<a href="%s" title="%s" meta-id="%s"class="directory-link"><li class="directory-item %s">%s</li></a>'
                % (
                    urllib.parse.quote(linkname, errors='surrogatepass'),
                    drive,
                    hash(drive),
                    classname,
                    drive
                )
                )
        r.append('</ul>')
        app = '\n'.join(r)
        title = "Home"
        page = template.format(
            style,
            preScript,
            app,
            postScript,
            title,
            title
        )
        encoded = page.encode(enc, 'surrogateescape')
        return encoded

    def list_search(self, path):
        term = urllib.parse.parse_qs(urllib.parse.urlparse(path))["q"]
        list = os.listdir(path)
        list.sort(key=lambda a: a.lower())
        r = []
        try:
            displaypath = urllib.parse.unquote(self.path,
                                               errors='surrogatepass')
        except UnicodeDecodeError:
            displaypath = urllib.parse.unquote(path)
        displaypath = html.escape(displaypath, quote=False)
        enc = sys.getfilesystemencoding()
        r.append('<ul class="directory-list">')
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                classname = "folder-item"
            else:
                classname = "file-item"
            if os.path.islink(fullname):
                classname = "folder-item"
                # Note: a link to a directory displays with @ and links with /
            r.append(
                '<a href="%s" title="%s" meta-name="%s" class="directory-link"><li class="directory-item %s">%s</li></a>'
                % (
                    urllib.parse.quote(linkname, errors='surrogatepass'),
                    html.escape(displayname, quote=False),
                    html.escape(displayname, quote=False),
                    classname,
                    html.escape(displayname, quote=False)
                )
                )
        r.append('</ul>')
        app = '\n'.join(r)
        navurl = "/"
        navitem = []
        navitem.append('<a href="%s" class="navpath">%s</a>'
                       % (
                           navurl,
                           "Home"
                       )
                       )
        for i in displaypath.split("/")[1:]:
            navurl += "%s/" % (i)
            navitem.append('<a href="%s" class="navpath">%s</a>'
                           % (
                               navurl,
                               i
                           )
                           )
        navhead = " &#x276D; ".join(navitem)
        title = " &#x276D; ".join(displaypath.split("/")[1:])
        page = template.format(
            style,
            preScript,
            app,
            postScript,
            navhead,
            title
        )
        encoded = page.encode(enc, 'surrogateescape')
        return encoded
