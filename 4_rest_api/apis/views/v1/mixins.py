from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response


class ProtectedDeleteMixin:
    #model ใช้ on_delete=PROTECT ถ้าไม่ดัก ProtectedError ไว้ DRF จะตอบ 500 เหมือนระบบพัง
    protected_error_detail = "This record is referenced by other data and cannot be deleted."

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": self.protected_error_detail},
                status=status.HTTP_409_CONFLICT,  #409 Conflict คือ status คำขอถูกต้องแต่สถานะปัจจุบันยังทำไม่ได้
            )
