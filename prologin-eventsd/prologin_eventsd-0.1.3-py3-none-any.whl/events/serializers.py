from rest_framework import (
    serializers,
)
from django.contrib.auth import get_user_model
from . import models


class CenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Center
        fields = (
            "id",
            "name",
            "address",
            "lng",
            "lat",
        )


class EventSerializer(serializers.ModelSerializer):

    center = CenterSerializer()

    class Meta:
        depth = 1
        model = models.Event
        fields = (
            "id",
            "name",
            "center",
            "signup_start_date",
            "signup_end_date",
            "start_date",
            "end_date",
            "form_id",
            "description",
            "notes",
            "documents",
        )


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Question
        fields = (
            "id",
            "order",
            "text",
            "type",
            "mandatory",
            "possible_answers",
        )


class FormSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many=True)

    class Meta:
        model = models.Form
        fields = (
            "id",
            "questions",
        )


class FormAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = models.FormAnswer
        fields = (
            "id",
            "question",
            "answer",
        )

        read_only_fields = ("id",)


class FormAnswerPushSerializer(serializers.ModelSerializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=models.Question.objects.all()
    )

    class Meta:
        model = models.FormAnswer
        fields = (
            "id",
            "question",
            "answer",
        )
        write_only_fields = ("attendee_id",)
        read_only_fields = ("id",)


class AttendeeSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        queryset=get_user_model().objects.all(),
    )

    status = serializers.ChoiceField(
        choices=models.SelectionStatus.choices,
        allow_null=True,
    )

    form_answers = FormAnswerPushSerializer(many=True)

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        validated_data["owner"] = user
        validated_data["status"] = models.SelectionStatus.ENROLLED.value
        form_answers = validated_data.pop("form_answers")
        ret = super().create(validated_data)
        for answer in form_answers:
            answer["attendee_id"] = ret.id
            FormAnswerPushSerializer().create(answer)
        return ret

    class Meta:
        model = models.Attendee
        fields = (
            "id",
            "owner",
            "event",
            "first_name",
            "last_name",
            "dob",
            "status",
            "form_answers",
        )

        read_only_fields = ("id",)
