from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from datetime import date, timedelta, datetime
from rest_framework import status
from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.vault import create_vault_client
from .models import (
    Infectionhistory,
    Closecontacts,
    Notifications
)
from .serializers import (
    CloseContactSerializer
)
from .utils import get_or_generate_secret_key, generate_temp_ids, decrypt_temp_id

# Create your views here.
class GenerateTemporaryIdsView(ListAPIView):

    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user_id = request.user.id
        print(type(user_id))
        vault_client = create_vault_client()
        temp_id_key = get_or_generate_secret_key(vault_client, settings.VAULT_TEMP_ID_KEY_PATH)
        temp_ids, start_time = generate_temp_ids(user_id, temp_id_key)
        payload = {
            'temp_ids': temp_ids,
            'server_start_time': start_time,
        }
        return Response(data=payload, status=status.HTTP_200_OK)


class UploadTemporaryIdsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    serializer_class = CloseContactSerializer

    def create(self, request):
        user_id = request.user.id

        user_recent_infection_history = Infectionhistory.objects.filter(
            user_id = user_id,
            recorded_timestamp__range=(
                date.today() - timedelta(days=15),
                date.today()
            ))
        if user_recent_infection_history.count() == 0:
            raise ValidationError('User has no recent infection history')
        
        user_recent_infection = user_recent_infection_history.latest("recorded_timestamp")
        
        notification = Notifications.objects.filter(infection_id=user_recent_infection.id, uploaded_status=False)
        if not notification.exists():
            raise ValidationError('User has no recent infection history')
        latest_notification = notification.latest('due_date')

        if latest_notification.due_date < datetime.now().date():
            raise ValidationError('User has no recent infection history')

        temp_ids = request.data.get('temp_ids')
        if temp_ids is None or type(temp_ids) != list or len(temp_ids) == 0:
            raise ValidationError('Missing temp_ids')
        
        vault_client = create_vault_client()
        temp_id_key = get_or_generate_secret_key(vault_client, settings.VAULT_TEMP_ID_KEY_PATH)
        final_temp_ids = list(filter(lambda x: decrypt_temp_id(x, temp_id_key, user_id, user_recent_infection.id), temp_ids))
        
        if len(final_temp_ids) == 0:
            raise ValidationError('No valid temp_ids')
        
        serial = self.serializer_class(data=final_temp_ids, many=True)
        serial.is_valid(raise_exception=True)

        latest_notification.uploaded_status = True
        serial.save()
        latest_notification.save()

        return Response(status=status.HTTP_201_CREATED)


class GetInfectionStatusView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        user_recent_infection_history = Infectionhistory.objects.filter(
            user_id = user_id,
            recorded_timestamp__range=(
                datetime.today() - timedelta(days=15),
                datetime.today()
            ))
        if user_recent_infection_history.count() > 0:
            return Response(data={'status': 'positive'}, status=status.HTTP_200_OK)

        user_recent_close_contact_history = Closecontacts.objects.filter(
            contacted_user_id = user_id,
            contact_timestamp__range=(
                datetime.today() - timedelta(days=15),
                datetime.today()
            )
        )

        if user_recent_close_contact_history.count() > 0:
            return Response(data={'status': 'close'}, status=status.HTTP_200_OK)

        return Response(data={'status': 'negative'}, status=status.HTTP_200_OK)


class GetUploadRequirementStatusView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        if Notifications.objects.filter(infection__user_id=user_id, start_date__lte=date.today(), due_date__gte=date.today(), uploaded_status=False).exists():
            return Response(data={'status': True}, status=status.HTTP_200_OK)
        return Response(data={'status': False}, status=status.HTTP_200_OK)