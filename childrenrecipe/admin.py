from django.contrib import admin
from .models import *

# Register your models here.


class MaterialInline(admin.TabularInline):
	model = Material
	extra = 1


class ProcedureInline(admin.TabularInline):
	model = Procedure
	extra = 1


class RecipeAdmin(admin.ModelAdmin):
	filter_horizontal = ('tag',)
	inlines = [
		MaterialInline,
		ProcedureInline,
	]
	list_display = ('id', 'name')


#admin.site.register(Student)
#admin.site.register(Classes)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Material)
admin.site.register(Procedure)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Recommend)


