import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            try:
                header, encoded = data.split(';base64,', 1)
            except ValueError:
                self.fail('invalid_image')
            ext = header.split('/')[-1]
            if ext == 'jpeg':
                ext = 'jpg'
            decoded = base64.b64decode(encoded)
            data = ContentFile(decoded, name=f'{uuid.uuid4()}.{ext}')
        return super().to_internal_value(data)