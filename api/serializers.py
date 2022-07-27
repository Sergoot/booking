from rest_framework import serializers
from .models import Visit, Client
from .tasks import send_email
from .services import generate_password
from django.contrib.auth import get_user_model
User = get_user_model()


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'email', 'name', 'phone')

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def create(self, validated_data):
        instance = User.objects.create_superuser(**validated_data, password=generate_password())
        self.fields['is_staff'] = serializers.BooleanField()
        return instance


class VisitSerializer(serializers.ModelSerializer):
    client = ClientSerializer(many=False, required=False)
    time_end = serializers.TimeField(required=False)

    class Meta:
        model = Visit
        fields = '__all__'

    def create(self, validated_data):
        email = validated_data.get('client').email
        date = validated_data.get('date').strftime('%x')
        time_start = validated_data.get('time_start').strftime('%H:%M')
        instance = Visit.objects.create(**validated_data)
        send_email.delay(email, date=date, time_start=time_start)
        return instance
