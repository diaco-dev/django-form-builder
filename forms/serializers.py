from rest_framework import serializers
from core.type import QuestionType
from .models import Form, Question, Option, Answer, Response, Attendance, Guest
from django.db import transaction
#------------------ADMIN------------------------------------------------#
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id','form','max','min', 'name','placeholder','description','category','text', 'question_type', 'is_required', 'order', 'options', '_created_at', '_updated_at', '_updated_by','_created_by']



class FormSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)
    class Meta:
        model = Form
        fields = ['id', 'title', 'type','questions','is_active','created_by', '_created_at', '_updated_at', '_updated_by','_created_by']


#------------------USER------------------------------------------------#
class UserQuestionSerializer(serializers.ModelSerializer):
    options = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Question
        fields = ['id','name','max','min', 'text','description','category','placeholder', 'question_type', 'is_required', 'options']


class UserFormSerializer(serializers.ModelSerializer):
    questions = UserQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = ['id','type', 'title', 'questions']


class AnswerSerializer(serializers.ModelSerializer):
    option = serializers.PrimaryKeyRelatedField(queryset=Option.objects.all(), required=False)
    question_details = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Answer
        fields = ['question','question_details', 'value', 'option']

    def get_question_details(self, obj):
        return UserQuestionSerializer(obj.question).data
    def validate(self, data):
        question = data['question']

        if question.question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.CHECKBOX]:
            if not data.get('option'):
                raise serializers.ValidationError("Option is required for this question type.")
            if data['option'].question_id != question.id:
                raise serializers.ValidationError("Selected option does not belong to this question.")

        return data


class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    form_title = serializers.CharField(source='form.title', read_only=True)
    class Meta:
        model = Response
        fields = ['id', 'form','form_title','user','day', 'answers','_created_at', '_updated_at', '_updated_by','_created_by']

    def validate(self, data):
        form = data['form']
        if not form.is_active:
            raise serializers.ValidationError("This form is not currently active.")


        required_questions = form.questions.filter(is_required=True).values_list('id', flat=True)
        answered_questions = {answer['question'].id for answer in data['answers']}
        missing = set(required_questions) - answered_questions
        if missing:
            raise serializers.ValidationError(f"Required questions missing: {missing}")
        return data

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        with transaction.atomic():
            response = Response.objects.create(**validated_data)
            for answer_data in answers_data:
                Answer.objects.create(response=response, **answer_data)
        return response

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', [])
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            existing_answers = {answer.question.id: answer for answer in instance.answers.all()}

            for answer_data in answers_data:
                question_id = answer_data['question'].id
                if question_id in existing_answers:

                    answer = existing_answers[question_id]
                    answer.value = answer_data['value']
                    answer.save()
                else:
                    Answer.objects.create(response=instance, **answer_data)

        return instance

class ResponseUserSerializer(serializers.ModelSerializer):
    form_title = serializers.CharField(source='form.title', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Response
        fields = ['id', 'form','first_name','last_name','form_title','user','_created_at', '_updated_at', '_updated_by','_created_by']

#------------------------------------------------------------------------------------------------------------#
class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['id','first_name', 'last_name','mobile', 'support_name', '_created_at','_created_by']


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    guest_details= GuestSerializer(many=True, read_only=True)
    class Meta:
        model = Attendance
        fields = ['id','form', 'day','guest','guest_details','student_name', 'student', 'status', '_created_at','_created_by']
