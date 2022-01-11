from django.contrib import admin
from django.conf import settings
from .models import *
from .views import bot
from django.shortcuts import redirect
import uuid


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'url', 'bon', 'status', 'create_at']
    list_display_links = list_display
    exclude = ['url_id']

    def save_model(self, request, obj, form, change) -> None:
        if obj.status:
            users = User.objects.all()
            if not obj.url_id:
                obj.url_id = uuid.uuid4()
                obj.save()
            for user in users:
                if user.chat_id and user not in obj.complite_users.all():
                    bot.send_message(user.chat_id, f'Задание: {obj.text}\nСылка: {settings.PROJECT_URL}/{user.id}/{obj.url_id}')
        return super().save_model(request, obj, form, change)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'phone', 'status']
    list_display_links = list_display
    readonly_fields = ['status']
    change_form_template = 'admin/changeform.html'

    def response_change(self, request, obj):
        if request.user.is_superuser:
            pay = Payment.objects.get(id=obj.id)
            if 'approve' in request.POST:
                pay.status = True
                pay.save()
                bot.send_message(pay.user.chat_id, f'Администратор подтвердил вашу заявку на сумму {pay.amount} KGS')
                self.message_user(request, 'Подтвержден')
                return redirect('admin/bot/payment/')
            elif 'disapprove' in request.POST:
                pay.status = False
                pay.save()
                bot.send_message(pay.user.chat_id, f'Администратор отклонил вашу заявку на сумму {pay.amount} KGS')
                self.message_user(request, 'Отклонен')
                return redirect('admin/bot/payment/')
        return super().response_change(request, obj)


admin.site.register(User)
