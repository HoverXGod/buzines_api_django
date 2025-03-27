from django.db import models
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta

class SalesFunnelManager(models.Manager):
    """Кастомный менеджер для работы с воронкой продаж"""
    
    def add_entry(self, user, product, stage, **kwargs):
        """
        Добавление новой записи в воронку
        """
        required_fields = {'user', 'product', 'stage'}
        if not all([user, product, stage]):
            raise ValueError("Missing required fields: user, product, stage")

        try:
            entry = self.model(
                user=user,
                product=product,
                stage=stage,
                category=product.category if product else None,
                device_type=kwargs.get('device_type', 'desktop'),
                session_data=kwargs.get('session_data', {}),
                order_item=kwargs.get('order_item')
            )
            entry.full_clean()
            entry.save()
            return entry
        except Exception as e:
            raise ValueError(f"Error creating funnel entry: {str(e)}")

    def update_entry(self, entry_id, **kwargs):
        """
        Обновление существующей записи
        """
        allowed_fields = {'stage', 'session_data', 'device_type', 'order_item'}
        try:
            entry = self.get(id=entry_id)
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(entry, field, value)
            entry.full_clean()
            entry.save()
            return entry
        except self.model.DoesNotExist:
            return None
        except Exception as e:
            raise ValueError(f"Error updating entry: {str(e)}")

    def get_entries(self, user=None, product=None, category=None, 
                  stage=None, days_back=30, limit=100):
        """
        Получение записей с фильтрами
        """
        filters = Q()
        
        if user:
            filters &= Q(user=user)
        if product:
            filters &= Q(product=product)
        if category:
            filters &= Q(category=category)
        if stage:
            filters &= Q(stage=stage)
            
        date_threshold = timezone.now() - timedelta(days=days_back)
        filters &= Q(timestamp__gte=date_threshold)

        return self.filter(filters)\
            .select_related('user', 'product', 'category')\
            .order_by('-timestamp')[:limit]