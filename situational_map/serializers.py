from rest_framework import serializers
from situational_map.models import MapLayout, MapObject

class MapLayoutSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    width = serializers.IntegerField(source='width_pixels', read_only=True)
    height = serializers.IntegerField(source='height_pixels', read_only=True)

    class Meta:
        model = MapLayout
        fields = [
            'id',
            'event',
            'name',
            'image',
            'image_url',
            'width',
            'height',
            'width_pixels',
            'height_pixels',
            'width_meters',
            'height_meters',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'width_pixels', 'height_pixels', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else ''

class MapObjectSerializer(serializers.ModelSerializer):
    layout = serializers.PrimaryKeyRelatedField(
        queryset=MapLayout.objects.all(),
        source='map_layout',
        required=False
    )
    object_type = serializers.CharField(source='obj_type')
    x_position = serializers.FloatField(source='x')
    y_position = serializers.FloatField(source='y')

    class Meta:
        model = MapObject
        fields = ['id', 'layout', 'map_layout', 'object_type', 'obj_type', 'x_position', 'y_position', 'x', 'y', 'label', 'metadata']
        read_only_fields = ['id']
        extra_kwargs = {
            'map_layout': {'write_only': True},
            'obj_type': {'write_only': True},
            'x': {'write_only': True},
            'y': {'write_only': True}
        }
