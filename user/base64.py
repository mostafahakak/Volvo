import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64FileField(serializers.FileField):
    def to_internal_value(self, data):
        if data:
            format, file = data.split(";base64,")
            ext = format.split("/")[-1]
            unique_id = uuid.uuid4()
            file = ContentFile(base64.b64decode(file), name=f"{unique_id.urn[9:]}.{ext}")
            return super(Base64FileField, self).to_internal_value(file)
        return data
