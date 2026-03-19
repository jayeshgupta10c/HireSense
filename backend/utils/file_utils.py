"""
utils/file_utils.py — Safe file handling helpers
"""
import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"pdf", "txt", "doc"}
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


def ensure_upload_dir():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file_storage) -> tuple[str, str]:
    """
    Save a werkzeug FileStorage object.
    Returns (saved_filename, original_name).
    Raises ValueError for disallowed extensions.
    """
    ensure_upload_dir()
    original_name = file_storage.filename or "unknown"
    if not allowed_file(original_name):
        raise ValueError(f"File type not allowed: {original_name}")

    ext = original_name.rsplit(".", 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, unique_name)
    file_storage.save(save_path)
    return unique_name, original_name


def get_file_path(filename: str) -> str:
    return os.path.join(UPLOAD_FOLDER, filename)


def delete_file(filename: str) -> bool:
    path = get_file_path(filename)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False