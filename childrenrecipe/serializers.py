from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *
from django.views.decorators.csrf import csrf_exempt
from . import config


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ('url', 'name')


class TagSerializer(serializers.HyperlinkedModelSerializer):
    category_name = serializers.CharField(source='category.name')

    class Meta:
        model = Tag
        fields = ('id', 'name', 'category_name')


class MaterialSerializer(serializers.ModelSerializer):
    recipe_title = serializers.CharField(source='recipe.name')

    class Meta:
        model = Material
        fields = ('url', 'id', 'recipe_title', 'name', 'portion')


class ProcedureSerializer(serializers.HyperlinkedModelSerializer):
    recipe = serializers.CharField(source='recipe.name')
    width = serializers.SerializerMethodField(read_only=True)
    height = serializers.SerializerMethodField(read_only=True)

    def get_width(self, obj):
        try:
            if hasattr(obj, 'image'):
                return obj.image.width
        except Exception, e:
            return 0

    def get_height(self, obj):
        try:
            if hasattr(obj, 'image'):
                return obj.image.height
        except Exception, e:
            return 0

    class Meta:
        model = Procedure
        fields = ('url', 'id', 'recipe', 'seq', 'describe', 'image', 'width', 'height')


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    tag = TagSerializer(many=True)
    material = MaterialSerializer(source='material_set', many=True)
    procedure = ProcedureSerializer(source='procedure_set', many=True)
    width = serializers.SerializerMethodField(read_only=True)
    height = serializers.SerializerMethodField(read_only=True)
    share_url = serializers.SerializerMethodField()

    def get_width(self, obj):
        try:
            if hasattr(obj, 'exihibitpic'):
                return obj.exihibitpic.width
        except Exception, e:
            return 0

    def get_height(self, obj):
        try:
            if hasattr(obj, 'exihibitpic'):
                return obj.exihibitpic.height
        except Exception, e:
            return 0

    def get_share_url(self, obj):
        return config.CARD_RECIPE_URL % obj.id

    class Meta:
        model = Recipe
        fields = ('url', 'id', 'name', 'user', 'exihibitpic', 'introduce', 'tag', 'tips',
                  'material', 'procedure', 'width', 'height', 'share_url'
                  )
