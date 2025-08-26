from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from forms.models import Response as ResponseModel
from utils.paginations import CustomLimitOffsetPagination
from .models import Form, Question, Option
from .serializers import FormSerializer, UserFormSerializer, ResponseSerializer, \
    QuestionSerializer, ResponseUserSerializer
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
#---------create -update -delete -----------------
class AdminFormViewSet(viewsets.ModelViewSet):
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_fields = ['_created_by','type']
    ordering_fields = ('_created_at', '_updated_at')
    search_fields = ('_created_by__first_name','_created_by__last_name','title')


    def perform_create(self, serializer):
        serializer.save(_created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(_created_by=self.request.user)

class QuestionCreateView(APIView):
    def post(self, request, form_id):
        try:
            form = Form.objects.get(id=form_id)
        except Form.DoesNotExist:
            return Response({'detail': 'Form not found'}, status=status.HTTP_404_NOT_FOUND)

        questions_data = request.data.get('questions', [])
        if not isinstance(questions_data, list) or not questions_data:
            return Response({'detail': 'Invalid or empty questions list'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = QuestionSerializer(data=questions_data, many=True)
        serializer.is_valid(raise_exception=True)

        created_questions = []
        for question_data in serializer.validated_data:
            options_data = question_data.pop('options', [])
            question = Question.objects.create(form=form, **question_data)
            options = [Option(question=question, **opt) for opt in options_data]
            Option.objects.bulk_create(options)
            created_questions.append(question)

        response_data = QuestionSerializer(created_questions, many=True).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class AdminQuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(_created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(_created_by=self.request.user)

#----------active form GET-----------------
class PublicFormViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Form.objects.filter(is_active=True)
    serializer_class = UserFormSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ['_created_by','type']
    ordering_fields = ('_created_at', '_updated_at')
#---------- bc get response ---------
class ResponseBcViewSet(viewsets.ModelViewSet):
    queryset = ResponseModel.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ['_created_by','user','day']
    ordering_fields = ('_created_at', '_updated_at')

    def get_queryset(self):
        return ResponseModel.objects.filter(_created_by=self.request.user)

#---------- user get response ---------
class ResponseViewSet(viewsets.ModelViewSet):
    queryset = ResponseModel.objects.all()
    serializer_class = ResponseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ['_created_by','user','form']
    ordering_fields = ('_created_at', '_updated_at')

    def get_queryset(self):
        if self.request.user.role in ['superuser', 'admin']:
            return ResponseModel.objects.all()
        return ResponseModel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ResponseUserViewSet(viewsets.ModelViewSet):
    queryset = ResponseModel.objects.all()
    serializer_class = ResponseUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ['_created_by','user','form']
    ordering_fields = ('_created_at', '_updated_at')


#---------- bc  ---------
class IsBusinessCoach(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'bc'
