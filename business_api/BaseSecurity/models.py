from django.db import models
from django.http import HttpRequest
from User.models import User

class AuditLog(models.Model):
    """Модель аудита, нужен для отладки и проверки пользователей"""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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
    def _write_audit(request: HttpRequest, action: str, error: str = None):
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
            "ERROR": error
        }

        if request.user.is_anonymous: 

            audit = AuditLog(
                action=action,
                details=details,
            ).save()
        else: 
            audit = AuditLog(
                user=user,
                action=action,
                details=details,
            ).save()

        return AuditLog.objects.last()