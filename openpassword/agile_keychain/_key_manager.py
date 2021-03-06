import os
import sys
import plistlib
from jinja2 import Template
from base64 import b64encode

from openpassword.agile_keychain._key import Key
from openpassword.exceptions import KeyAlreadyExistsForLevelException, InvalidKeyFileException

DEFAULT_ITERATIONS = 25000

# plistlib loading method name changed in Python 3.4.0, but the signature
# remained the same, so simply refer to the old method by new name in older
# Python versions
if sys.version_info < (3, 4, 0):
    plistlib.loads = plistlib.readPlistFromBytes


class KeyManager:
    def __init__(self, path):
        self._base_path = path

    def get_keys(self):
        return self._read_keys_from_keys_plist()

    def create_key(self, password, security_level='SL5', iterations=DEFAULT_ITERATIONS):
        return Key.create(password, security_level, iterations)

    def save_key(self, new_key):
        existing_keys = self._read_keys_from_keys_plist()

        keys = []
        for old_key in existing_keys:
            if old_key.identifier == new_key.identifier:
                continue

            if old_key.security_level == new_key.security_level:
                raise KeyAlreadyExistsForLevelException()

            keys.append(old_key)

        keys.append(new_key)
        keys = [self._serialize_key(key) for key in keys]

        template_path = os.path.join(os.path.dirname(__file__), '1password.keys.template')

        with open(template_path, 'r') as file:
            plist_template = Template(file.read())

        with open(os.path.join(self._base_path, 'data', 'default', '1password.keys'), 'w') as file:
            file.write(plist_template.render({'keys': keys}))

    def _serialize_key(self, key):
        return {
            'identifier': key.identifier,
            'iterations': key.iterations,
            'data': (b64encode(key.data) + b'\x00').decode('ascii'),
            'validation': (b64encode(key.validation) + b'\x00').decode('ascii'),
            'level': key.security_level
        }

    def _read_keys_from_keys_plist(self):
        plist_contents = self._load_keys_plist()

        if len(plist_contents) == 0:
            return []

        keys = self._parse_plist(plist_contents)

        return [Key(key) for key in keys['list']]

    def _load_keys_plist(self):
        if os.path.exists(os.path.join(self._base_path, 'data', 'default', '1password.keys')) is False:
            return None

        with open(os.path.join(self._base_path, 'data', 'default', '1password.keys'), 'rb') as file:
            data = file.read()

        return self._remove_null_bytes(data)

    def _parse_plist(self, plist_contents):
        try:
            return plistlib.loads(plist_contents)
        except plistlib.InvalidFileException:
            raise InvalidKeyFileException

    def _remove_null_bytes(self, data):
        result = b''
        last = 0

        index = data.find(b'\x00')
        while index != -1:
            result = result + data[last:index]
            last = index + 1
            index = data.find(b'\x00', last)

        result = result + data[last:]

        return result
