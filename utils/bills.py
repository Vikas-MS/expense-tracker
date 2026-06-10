import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename


def get_user_bill_dir(user_id):
    return os.path.join(current_app.config['UPLOAD_FOLDER'], user_id)


def get_bill_filepath(user_id, stored_name):
    return os.path.join(get_user_bill_dir(user_id), stored_name)


def validate_bill_file(file):
    if not file or not file.filename:
        return None

    original_name = secure_filename(file.filename)
    if not original_name or '.' not in original_name:
        raise ValueError('Invalid file name')

    ext = original_name.rsplit('.', 1)[1].lower()
    allowed = current_app.config.get('ALLOWED_BILL_EXTENSIONS', set())
    if ext not in allowed:
        raise ValueError('Invalid file type. Allowed: PDF, PNG, JPG, JPEG, WEBP')

    return original_name, ext


def save_bill(file, user_id):
    validated = validate_bill_file(file)
    if not validated:
        return None

    original_name, ext = validated
    stored_name = f'{uuid.uuid4()}.{ext}'
    user_dir = get_user_bill_dir(user_id)
    os.makedirs(user_dir, exist_ok=True)
    filepath = os.path.join(user_dir, stored_name)
    file.save(filepath)

    return {
        'bill_filename': stored_name,
        'bill_original_name': original_name,
        'bill_mime_type': file.content_type or '',
        'bill_size': os.path.getsize(filepath),
    }


def delete_bill_file(user_id, stored_name):
    if not stored_name:
        return
    filepath = get_bill_filepath(user_id, stored_name)
    if os.path.exists(filepath):
        os.remove(filepath)


def apply_bill_data(transaction, bill_data):
    if not bill_data:
        return
    transaction.bill_filename = bill_data['bill_filename']
    transaction.bill_original_name = bill_data['bill_original_name']
    transaction.bill_mime_type = bill_data['bill_mime_type']
    transaction.bill_size = bill_data['bill_size']


def clear_bill_data(transaction):
    transaction.bill_filename = None
    transaction.bill_original_name = None
    transaction.bill_mime_type = None
    transaction.bill_size = None
