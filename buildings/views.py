from django.shortcuts import render
from .models import Buildings, Buildingaccess, Users
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date, datetime, timedelta
from .serializers import BuildingRegisterSerializer
import qrcode
import io
import base64

import logging
logger = logging.getLogger('loki')

# Create your views here.

class GenerateQRCodeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            building = Buildings.objects.get(name=kwargs['name'])
        except Buildings.DoesNotExist:
            raise ValidationError(detail="Building does not exist")
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(building.id)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        tmp = io.BytesIO()
        img_save = img.save(tmp)
        png_qr = tmp.getvalue()
        b64_img = base64.b64encode(png_qr)
        logger.info('Generated Building QR code.', extra={'action': 'generate_building_qr_code', 'request': request, 'building_id': building.id})
        return Response(data={"qrcode": b64_img}, status=status.HTTP_200_OK)

class BuildingAccessRegister (CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            user = Users.objects.get(id=request.user.id)
        except Users.DoesNotExist:
            raise ValidationError(detail="User does not exist")
        try:
            building = Buildings.objects.get(id=request.data['building'])
        except:
            logger.warn('Building does not exist.', extra={'action': 'building_access', 'request': request, 'user_id': user.id})
            raise ValidationError(detail="Building does not exist")
            
        infection = user.infectionhistory_set.filter( 
            recorded_timestamp__range=(datetime.combine(date.today(), datetime.min.time())-timedelta(days=15), datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999))
            )
        if infection.exists():
            logger.info('User has recent infection history.', extra={'action': 'building_access', 'request': request, 'user_id': user.id})
            return Response(data={'building_name': building.name, 'infected':True}, status=status.HTTP_200_OK)

        request.data['user'] = request.user.id
        request.data['access_timestamp'] = datetime.now()
        buildingaccess = BuildingRegisterSerializer(data=request.data)
        buildingaccess.is_valid(raise_exception=True)
        buildingaccess.save()

        logger.info('User accessed building.', extra={'action': 'building_access', 'request': request, 'user_id': request.user.id, 'building_id': building.id})

        return Response(data={'building_name': building.name, 'infected': False}, status=status.HTTP_201_CREATED)
