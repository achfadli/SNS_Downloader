import os

# Struktur folder dan file yang akan dibuat
structure = {
    "video_downloader": {
        "__init__.py": "",
        "settings": {
            "__init__.py": "",
            "base.py": "",
            "development.py": "",
            "production.py": ""
        },
        "urls.py": "",
        "wsgi.py": "",
        "asgi.py": "",
    },
    "apps": {
        "FacebookD": {
            "__init__.py": "",
            "admin.py": "",
            "apps.py": "",
            "models.py": "",
            "tests.py": "",
            "views.py": "",
            "urls.py": "",
            "forms.py": "",
            "migrations": {}
        },
        "PintD": {
            "__init__.py": "",
            "admin.py": "",
            "apps.py": "",
            "models.py": "",
            "tests.py": "",
            "views.py": "",
            "urls.py": "",
            "forms.py": "",
            "migrations": {}
        },
        "TiktokD": {
            "__init__.py": "",
            "admin.py": "",
            "apps.py": "",
            "models.py": "",
            "tests.py": "",
            "views.py": "",
            "urls.py": "",
            "forms.py": "",
            "migrations": {}
        },
        "YoutubeD": {
            "__init__.py": "",
            "admin.py": "",
            "apps.py": "",
            "models.py": "",
            "tests.py": "",
            "views.py": "",
            "urls.py": "",
            "forms.py": "",
            "migrations": {}
        },
    },
    "manage.py": "",
    "db.sqlite3": ""
}


def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            with open(path, 'w') as f:
                f.write(content)


# Tentukan path dasar untuk proyek
base_path = "Pintarest Downloader"
create_structure(base_path, structure)

print("Struktur folder dan file telah dibuat.")
