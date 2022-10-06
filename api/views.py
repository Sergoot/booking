from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser
from .serializers import VisitSerializer, ClientSerializer, ClientDetailSerializer
from .models import Visit, Client
from .services import get_all_or_filter, get_or_create, get_end_time, generate_password, send_websocket_notice
from .permissions import IsOwnerOrAdminUser
from django.db.models import QuerySet
from .tasks import send_email
from datetime import datetime


class VisitViewSet(viewsets.ModelViewSet):
    """ ViewSet Приёма """
    serializer_class = VisitSerializer

    def get_permissions(self):
        if self.action == 'create' or self.action == 'get_busy_time':
            return [AllowAny(), ]
        return [IsOwnerOrAdminUser(), ]

    def get_queryset(self) -> QuerySet:
        if self.action == 'list':
            date = self.request.query_params.get('date')
            if date:
                return get_all_or_filter(Visit, date=date).order_by('time_start')
            return get_all_or_filter(Visit, date=datetime.today().date()).order_by('time_start')
        return get_all_or_filter(Visit)

    def perform_create(self, serializer) -> dict | None:
        data = self.request.data
        time_start = data.get('time_start')
        date = data.get('date')
        email = data.get('email')
        if not list(get_all_or_filter(Visit, time_start=time_start, date=date)):
            client, is_created = get_or_create(Client, email=email)
            duration = data.get('duration', 60)
            if is_created:
                password = generate_password()
                client.set_password(password)
                client.save()
                client_serializer = ClientSerializer(data=data, instance=client)
                client_serializer.is_valid(raise_exception=True)
                client_serializer.save()
                send_email.delay(email, password)
            time_end = get_end_time(time_start, duration)
            serializer.is_valid(raise_exception=True)
            vizit_data = {**serializer.validated_data, 'time_end': time_end, 'client': client}

            serializer.save(**vizit_data)
        else:
            return {'error_message': 'Запись на данное время недоступна'}

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        perform_create_result = self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        if perform_create_result is None:
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(perform_create_result, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def get_busy_time(self, request) -> Response:
        date = request.query_params.get("date").split(',')
        time_start = request.query_params.get("time_start").split(',')
        queryset = get_all_or_filter(Visit, date__in=date, time_start__in=time_start)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True)
    def client_visits(self, request, pk=None) -> Response:
        """ Список всех записей клиента """
        visited = self.request.query_params.get('visited')
        queryset = get_all_or_filter(Visit, client=pk).order_by('is_visited', 'date', 'time_start')
        if visited:
            queryset = queryset.filter(is_visited=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    """ ViewSet Клиента """
    serializer_class = ClientDetailSerializer
    queryset = get_all_or_filter(Client, is_staff=False)
    # permission_classes = (IsAdminUser, )

    @action(methods=['get'], detail=False)
    def admins(self, request) -> Response:
        """ Список админов """
        queryset = get_all_or_filter(Client, is_staff=True,)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs) -> Response:
        """ Создание админа """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['post'],)
    def password(self, request):
        req_pass = request.data.get('password')
        print(req_pass)
        password = request.user.password
        print(req_pass == password)
        return Response({'password': password})
