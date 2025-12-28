from django.core.management.base import BaseCommand
from tienda.models import Producto, Fabricante, Cat_Colegio, Cat_Tipo, Cat_Sexo
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.conf import settings
import requests
import random
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de prueba para la tienda'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando proceso de seeding...')

        # 1. Crear Usuario Admin y Fabricante
        # 1. Crear Usuario Admin y Fabricante
        admin_user, created = User.objects.get_or_create(
            email='admin@seed.com',
            defaults={
                'nombre': 'Admin',
                'apellido': 'Seed',
                'rut': '11.111.111-1', 
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario creado: {admin_user.email}'))

        fabricante, created = Fabricante.objects.get_or_create(
            nombre='Confecciones Seed',
            defaults={'usuario': admin_user}
        )

        # 2. Categorías Maestras
        colegios_data = [
            ('SANJO', 'Colegio San José', 'bg-blue-800', '1e3a8a'),
            ('STAMA', 'Colegio Santa María', 'bg-red-800', '991b1b'),
            ('ANDES', 'Instituto Andes', 'bg-green-800', '065f46'),
        ]
        
        colegios = {}
        for code, name, color_cls, hex_color in colegios_data:
            obj, _ = Cat_Colegio.objects.get_or_create(
                codigo=code, 
                defaults={'nombre': name, 'descripcion': f'Uniformes oficiales {name}'}
            )
            colegios[code] = (obj, hex_color)

        tipos_data = [
            ('POL', 'Polera', 'Piqué algodón'),
            ('PAN', 'Pantalón', 'Gris marengo'),
            ('FAL', 'Falda', 'Plisada escocesa'),
            ('POLG', 'Polerón', 'Algodón con cierre'),
            ('PAR', 'Parka', 'Impermeable térmica'),
        ]
        tipos = {}
        for code, name, desc in tipos_data:
            obj, _ = Cat_Tipo.objects.get_or_create(
                codigo=code,
                defaults={'nombre': name, 'descripcion': desc}
            )
            tipos[code] = obj

        sexos_data = [
            ('H', 'Niño', 'Corte masculino'),
            ('M', 'Niña', 'Corte femenino'),
            ('U', 'Unisex', 'Corte recto'),
        ]
        sexos = {}
        for code, name, desc in sexos_data:
            obj, _ = Cat_Sexo.objects.get_or_create(
                codigo=code,
                defaults={'nombre': name, 'descripcion': desc}
            )
            sexos[code] = obj

        # 3. Productos
        # Limpiar productos existentes creados por este seed (opcional, por ahora aditivo simple)
        # Producto.objects.filter(sku__startswith='SEED-').delete()

        productos_specs = [
            # San Jose (Azul)
            ('SANJO', 'POL', 'U', 'Polera Piqué San José', 12990),
            ('SANJO', 'PAN', 'H', 'Pantalón Gris San José', 18990),
            ('SANJO', 'FAL', 'M', 'Falda Escocesa San José', 16990),
            ('SANJO', 'POLG', 'U', 'Polerón Institucional', 22990),
            
            # Santa Maria (Rojo)
            ('STAMA', 'POL', 'M', 'Blusa Blanca Santa María', 13990),
            ('STAMA', 'FAL', 'M', 'Jumper Azul Marino', 19990),
            ('STAMA', 'POLG', 'U', 'Polerón Rojo Corporativo', 21990),
            
            # Andes (Verde)
            ('ANDES', 'POL', 'U', 'Polera Deportiva Andes', 11990),
            ('ANDES', 'PAR', 'U', 'Parka Térmica Verde', 34990),
        ]

        count = 0
        for col_code, tipo_code, sex_code, nombre, precio in productos_specs:
            colegio_obj, hex_color = colegios[col_code]
            tipo_obj = tipos[tipo_code]
            sex_obj = sexos[sex_code]
            
            # Generar SKU unico
            sku = f"{col_code}-{tipo_code}-{sex_code}-{random.randint(100,999)}"
            
            if Producto.objects.filter(nombre=nombre).exists():
                continue

            # Generar imagen Mock
            # Usamos placehold.co con colores personalizados
            img_url = f"https://placehold.co/600x800/{hex_color}/ffffff/png?text={nombre.replace(' ', '+')}"
            
            try:
                response = requests.get(img_url, timeout=10)
                if response.status_code == 200:
                    prod = Producto(
                        nombre=nombre,
                        sku=sku,
                        precio=precio,
                        cat_colegio=colegio_obj,
                        cat_tipo=tipo_obj,
                        cat_sexo=sex_obj,
                        fabricante=fabricante,
                        stock=random.randint(10, 100),
                        disponibilidad=True
                    )
                    # Guardar imagen
                    filename = f"{sku}.png"
                    prod.imagen.save(filename, ContentFile(response.content), save=False)
                    prod.save()
                    
                    self.stdout.write(f"Creado: {nombre}")
                    count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creando {nombre}: {e}"))

        self.stdout.write(self.style.SUCCESS(f'Seeding completado! {count} productos creados.'))
