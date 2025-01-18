# admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import GoogleCredentials, Lecture


class GoogleCredentialsAdmin(admin.ModelAdmin):
    change_list_template = "admin/google_credentials_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('authorize/', self.admin_site.admin_view(self.authorize),
                 name='google_authenticate'),
        ]
        return custom_urls + urls

    def authorize(self, request):
        return redirect('google_authenticate')

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['authorize_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

    # def render_change_form(self, request, context, *args, **kwargs):
    #     context['adminform'].form.fields['client_secret'].widget.attrs['readonly'] = True
    #     return super().render_change_form(request, context, *args, **kwargs)


admin.site.register(GoogleCredentials, GoogleCredentialsAdmin)
admin.site.register(Lecture)
