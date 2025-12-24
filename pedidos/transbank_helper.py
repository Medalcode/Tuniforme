# pedidos/transbank_helper.py
"""
Helper para configurar Transbank según el ambiente.
"""
from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType


def get_transbank_options():
    """
    Retorna las opciones de Transbank según el ambiente configurado.
    
    Returns:
        WebpayOptions: Configuración de Transbank
    """
    config = settings.TRANSBANK_CONFIG
    integration_type = (
        IntegrationType.LIVE 
        if config['environment'] == 'production' 
        else IntegrationType.TEST
    )
    
    return WebpayOptions(
        commerce_code=config['commerce_code'],
        api_key=config['api_key'],
        integration_type=integration_type
    )


def get_transbank_transaction():
    """
    Retorna una instancia de Transaction configurada.
    
    Returns:
        Transaction: Instancia de transacción de Transbank
    """
    return Transaction(get_transbank_options())
