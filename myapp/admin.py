from django.contrib import admin
from .models import CustomUser, Hospital, MedicationMaster, MedicinePrescription, Appointment, AppointmentSlot, Prescription, Doctor, AppointmentHistory
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(AppointmentSlot)
admin.site.register(Prescription)
admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(AppointmentHistory)
admin.site.register(MedicinePrescription)
admin.site.register(MedicationMaster)
admin.site.register(Hospital)