from django.conf.urls import url

import views

urlpatterns = [
    url(r'^$', views.HomepageView.as_view(), name="homepage"),
    url(r'^data/$', views.AJAXDataView.as_view(), name="data"),
]
