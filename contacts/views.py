from django.conf import settings
from django.shortcuts import render
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.response import Response
from datetime import date, timedelta, datetime
from rest_framework import status
from django.http import Http404
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.vault import create_vault_client
from .utils import get_or_generate_secret_key, generate_temp_ids, decrypt_temp_ids

# Create your views here.
class GenerateTemporaryIdsView(ListAPIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_id = request.user.id
        print(type(user_id))
        vault_client = create_vault_client()
        temp_id_key, start_time = get_or_generate_secret_key(vault_client, settings.VAULT_TEMP_ID_KEY_PATH)
        payload = {
            'temp_ids': generate_temp_ids(user_id, temp_id_key),
            'server_start_time': start_time,
        }
        return Response(data=payload, status=status.HTTP_200_OK)

