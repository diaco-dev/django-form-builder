from rest_framework.routers import DefaultRouter
from django.urls import path, include
from forms import views
from forms.views import QuestionCreateView

router = DefaultRouter()
router.register(r'admin/forms', views.AdminFormViewSet,basename='admin_form')
router.register(r'admin/question', views.AdminQuestionViewSet,basename='admin_qa')
router.register(r'forms',views.PublicFormViewSet,basename='view_form')
router.register(r'bc/response', views.ResponseBcViewSet,basename='bc_response_student')
router.register(r'response', views.ResponseViewSet,basename='admin_response')
router.register(r'admin/user-response', views.ResponseUserViewSet,basename='admin_response_user')
router.register(r'bc/attendance', views.AttendanceViewSet,basename='bc_attendance')
router.register(r'bc/guest', views.GuestViewSet,basename='bc_guest')


app_name = 'forms'

urlpatterns = [
    path('', include(router.urls)),
    path('question-create/<uuid:form_id>/', QuestionCreateView.as_view(), name='bulk_create_form_question'),

]
