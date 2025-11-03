from django.db import models
from django.http import HttpRequest

class AuditLog(models.Model):
    """Модель аудита, нужен для отладки и проверки пользователей"""

    user = models.ForeignKey('User.User', on_delete=models.SET_NULL, null=True, related_name='visits')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField()
    status = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Аудит'  # Имя модели в единственном числе
        verbose_name_plural = 'Аудиты'  # Имя модели во множественном числе

    @property
    def request_status(self) -> int: return self.status

    @request_status.setter
    def request_status(self, value): 
        self.status = value
        super().save()

    @staticmethod
    def _write_audit(request: HttpRequest, action: str):
        """Записываем аудит в базу данных"""

        user = request.user
        session = dict(request.session.items())
        COOKIES = request.COOKIES
        POST = request.POST.dict()
        GET = request.GET.dict()

        try: del session['_menus']
        except: pass

        SESSION = session

        action = "".join(action.split("?")[0])

        details = {
            "SESSION": SESSION,
            "COOKIES": COOKIES,
            "GET": GET,
            "POST": POST,
        }

        if request.user.is_anonymous: 

            AuditLog(
                action=action,
                details=details,
            ).save()
        else: 
            AuditLog(
                user=user,
                action=action,
                details=details,
            ).save()

        return AuditLog.objects.last()

class ExceptionManager(models.Model):
    exception_string = models.CharField(max_length=2048)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ошибка'  # Имя модели в единственном числе
        verbose_name_plural = 'Ошибки'  # Имя модели во множественном числе

    @staticmethod
    def register_exception(error: Exception) -> None:
        ExceptionManager(exception_string = str(error)).save()