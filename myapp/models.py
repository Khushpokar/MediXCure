from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model extending Django's AbstractUser
class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def _str_(self):
        return self.username

# Hospital model to store hospital information
class Hospital(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    photo = models.ImageField(upload_to='hospital_photos/', null=True, blank=True)

    def _str_(self):
        return self.name

# Doctor model linked to CustomUser, but only users with is_doctor=True can be doctors
class Doctor(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50, unique=True)
    years_of_experience = models.PositiveIntegerField()
    qualification = models.CharField(max_length=255)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

    def _str_(self):
        return f'Dr. {self.user.first_name} {self.user.last_name}'

# Appointment Slot model to store time slots for appointments
class AppointmentSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('available', 'Available'), ('booked', 'Booked')], default='available')

    def _str_(self):
        return f'Appointment with {self.doctor} at {self.start_time}'

# Appointment model to store actual appointments
class Appointment(models.Model):
    appointment_slot = models.ForeignKey(AppointmentSlot, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def _str_(self):
        return f'Appointment for {self.user} with {self.appointment_slot.doctor}'

# Appointment History model to store appointment records
class AppointmentHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointment_history')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointment_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()

    def _str_(self):
        return f'Appointment history of {self.user} with {self.doctor} on {self.date}'

# Prescription model linked to an appointment history
class Prescription(models.Model):
    appointment_history = models.ForeignKey(AppointmentHistory, on_delete=models.CASCADE)
    notes = models.TextField()

    def _str_(self):
        return f'Prescription for appointment history ID {self.appointment_history.id}'

# Medication Master model to store information about medicines
from django.db import models

class MedicationMaster(models.Model):
    # Enum for Dosage Form
    class DosageFormChoices(models.TextChoices):
        CREAM = 'Cream', 'Cream'
        INJECTION = 'Injection', 'Injection'
        OINTMENT = 'Ointment', 'Ointment'
        SYRUP = 'Syrup', 'Syrup'
        TABLET = 'Tablet', 'Tablet'
        INHALER = 'Inhaler', 'Inhaler'
        CAPSULE = 'Capsule', 'Capsule'
        DROPS = 'Drops', 'Drops'
    
    # Enum for Indication
    class IndicationChoices(models.TextChoices):
        VIRUS = 'Virus', 'Virus'
        INFECTION = 'Infection', 'Infection'
        WOUND = 'Wound', 'Wound'
        PAIN = 'Pain', 'Pain'
        FUNGUS = 'Fungus', 'Fungus'
        DIABETES = 'Diabetes', 'Diabetes'
        DEPRESSION = 'Depression', 'Depression'
        FEVER = 'Fever', 'Fever'

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    
    # Use the choices feature for dosage form
    dosage_form = models.CharField(
        max_length=50,
        choices=DosageFormChoices.choices,
        default=DosageFormChoices.TABLET  # Default to 'Tablet'
    )

    strength = models.CharField(max_length=50)  # e.g., 500mg
    manufacturer = models.CharField(max_length=255)
    
    # Use the choices feature for indication
    indication = models.CharField(
        max_length=50,
        choices=IndicationChoices.choices,
        default=IndicationChoices.PAIN  # Default to 'Pain'
    )
    
    classification = models.CharField(max_length=255)  # e.g., Antibiotic

    def _str_(self):
        return self.name

# pip install django-multiselectfield
# install this first

# Medicine Prescription model linking prescriptions to medicines
from django.db import models
from multiselectfield import MultiSelectField

class MedicinePrescription(models.Model):
    # Enum for frequency
    class FrequencyChoices(models.TextChoices):
        MORNING = 'Morning', 'Morning'
        AFTERNOON = 'Afternoon', 'Afternoon'
        EVENING = 'Evening', 'Evening'
        NIGHT = 'Night', 'Night'
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='medicines')
    medicine = models.ForeignKey(MedicationMaster, on_delete=models.CASCADE)
    dosage = models.CharField(max_length=100)
    
    # Frequency of medication, limited to morning, afternoon, evening, night
    frequency = models.CharField(
        max_length=50,
        choices=FrequencyChoices.choices,
        default=FrequencyChoices.MORNING
    )
    
    # Use MultiSelectField for 'when' field, allowing multiple times to be selected
    WHEN_CHOICES = [
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Evening', 'Evening'),
        ('Night', 'Night'),
    ]
    when = MultiSelectField(choices=WHEN_CHOICES, null=True, blank=True)

    def _str_(self):
        return f'{self.medicine.name} prescribed in {self.prescription.id}'