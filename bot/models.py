from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    user_id = models.CharField(_('User ID'), max_length=255, null=True, unique=True)
    chat_id = models.CharField(_('Chat ID'), max_length=255, null=True, unique=True)
    balance = models.DecimalField(_('Balance'), max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.username


class Payment(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='User',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Сумма: ',
        null=True
    )
    date = models.DateTimeField(
        verbose_name='Дата',
        auto_now_add=True
    )
    status = models.BooleanField(
        verbose_name='Статус',
        default=False
    )
    phone = models.CharField(_('Номер телефона'), max_length=25, default='None')

    class Meta:
        verbose_name = 'Заявки для вывода'
        verbose_name_plural = 'Заявки для вывода'

    def __str__ (self):
        return str(self.user)


class Task(models.Model):
    text = models.TextField(
        verbose_name='Текст задачи'
    )
    url = models.URLField(
        verbose_name='URL задачи'
    )
    create_at = models.DateTimeField(
        verbose_name='Создано',
        auto_now_add=True
    )
    bon = models.PositiveIntegerField(
        verbose_name='Сумма для выполнения',
        default=0
    )
    status = models.BooleanField(
        verbose_name='Статус',
        default=True
    )
    url_id = models.UUIDField(blank=True)
    complite_users = models.ManyToManyField(User, verbose_name=_('Complite users'), blank=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return str(self.id)
