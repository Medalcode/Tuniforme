from django.contrib import admin
from .models import Producto, Cat_Tipo, Cat_Colegio, Cat_Sexo

class ProductoAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'precio', 'stock', 'disponibilidad', 'fabricante')
    search_fields = ('nombre', 'fabricante__nombre')
    list_filter = ('disponibilidad', 'cat_colegio', 'cat_tipo', 'cat_sexo')
    ordering = ('nombre',)

class Cat_TipoAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')

class Cat_ColegioAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')

class Cat_SexoAdmin(admin.ModelAdmin):
    readonly_fields = ('creado', 'actualizado')
    list_display = ('nombre', 'codigo')
    search_fields = ('nombre', 'codigo')

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cat_Tipo, Cat_TipoAdmin)
admin.site.register(Cat_Colegio, Cat_ColegioAdmin)
admin.site.register(Cat_Sexo, Cat_SexoAdmin)