from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

import models


class TransferenciaCreate(BaseModel):
    """Esquema para la creación de una transferencia (POST)."""
    producto_id: int
    sucursal_origen_id: int
    sucursal_destino_id: int
    cantidad_solicitada: int = Field(gt=0)
    urgencia: models.UrgenciaTransferencia = models.UrgenciaTransferencia.MEDIA
    observaciones: Optional[str] = None


class TransferenciaPreparar(BaseModel):
    """Esquema para preparar una transferencia (POST)."""
    cantidad_enviada: int = Field(gt=0)


class TransferenciaDespachar(BaseModel):
    """Esquema para despachar una transferencia (POST)."""
    transportista: str = Field(min_length=1, max_length=100)
    fecha_estimada_llegada: Optional[datetime] = None


class TransferenciaRecepcion(BaseModel):
    """Esquema para la recepción de una transferencia (POST)."""
    cantidad_recibida: int = Field(gt=0)
    tratamiento_faltante: Optional[models.TratamientoFaltante] = None
    observaciones_recepcion: Optional[str] = None


class AlertaOut(BaseModel):
    """Esquema para la representación de una alerta que la API DEVUELVE (GET, y tambien la respuesta de POST/PUT)."""
    id: int
    tipo: models.TipoAlerta
    producto_id: Optional[int]
    sucursal_id: int
    transferencia_id: Optional[int]
    mensaje: str
    resuelta: bool
    fecha_registro: datetime

    class Config:
        from_attributes = True


class TransferenciaOut(BaseModel):
    """Esquema para la representación de una transferencia que la API DEVUELVE (GET, y tambien la respuesta de POST/PUT)."""
    id: int
    producto_id: int
    sucursal_origen_id: int
    sucursal_destino_id: int
    cantidad_solicitada: int
    cantidad_enviada: Optional[int]
    cantidad_recibida: Optional[int]
    cantidad_faltante: Optional[int]
    estado: models.EstadoTransferencia
    urgencia: models.UrgenciaTransferencia
    transportista: Optional[str]
    fecha_solicitud: datetime
    fecha_estimada_llegada: Optional[datetime]
    fecha_envio: Optional[datetime]
    fecha_recepcion: Optional[datetime]
    usuario_solicita_id: int
    observaciones: Optional[str]
    tratamiento_faltante: Optional[models.TratamientoFaltante]
    observaciones_recepcion: Optional[str]
    alertas: list[AlertaOut] = []

    class Config:
        from_attributes = True
