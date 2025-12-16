from django.db import models
from django.utils.translation import gettext_lazy as _
from .core import Employee
from horilla.models import PetabytzModel, upload_path

class EmployeeIDProof(PetabytzModel):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="id_proof",
        verbose_name=_("Employee")
    )
    aadhar_front = models.ImageField(upload_to=upload_path, verbose_name=_("Aadhar Card Front"))
    aadhar_back = models.ImageField(upload_to=upload_path, verbose_name=_("Aadhar Card Back"))
    pan_card = models.ImageField(upload_to=upload_path, verbose_name=_("PAN Card"))
    
    is_locked = models.BooleanField(default=False, verbose_name=_("Is Locked"))

    def __str__(self):
        return f"{self.employee} - ID Proofs"
    
    class Meta:
        verbose_name = _("Employee ID Proof")
        verbose_name_plural = _("Employee ID Proofs")
