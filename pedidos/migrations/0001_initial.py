# Generated by Django 5.1.4 on 2024-12-18 04:57

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DetallePedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.PositiveIntegerField(default=1)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('precio_unitario', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('finalizado', models.BooleanField(default=False)),
                ('comision', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('total_fabricante', models.DecimalField(decimal_places=2, editable=False, max_digits=10)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'DetallePedido',
                'verbose_name_plural': 'DetallePedidos',
                'db_table': 'tDetallePedidos',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('finalizado', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
                'db_table': 'tPedidos',
            },
        ),
    ]
