import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Hospital, Doctor, AppointmentSlot, Appointment, AppointmentHistory, Prescription, MedicationMaster, MedicinePrescription
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
# User Signup



@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            username = data.get('username')
            password = data.get('password')
            date_of_birth = data.get('date_of_birth')
            gender = data.get('gender')

            # Log the username
            print(f'Username: {username}')

            # Check for required fields
            if not username:
                return JsonResponse({'error': 'Username is required.'}, status=400)

            # Check if username or email already exists
            if CustomUser.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already taken.'}, status=400)

            if CustomUser.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Email already exists.'}, status=400)

            # Create the user
            user = CustomUser.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=make_password(password),
                date_of_birth=date_of_birth,
                gender=gender
            )

            # Return a response including user details
            return JsonResponse({
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'username': user.username,
                    'date_of_birth': user.date_of_birth,
                    'gender': user.gender
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            username = data.get('username')
            password = data.get('password')

            # Authenticate user
            user = authenticate(username=username, password=password)

            if user is not None:
                # Determine the user's role
                role = Doctor.objects.filter(user=user).first()
                role_name = 'D' if role else 'P'

                login(request, user)

                # Return full user information
                user_data = {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'username': user.username,
                    'date_of_birth': user.date_of_birth,  # Ensure date_of_birth exists in your user model
                    'gender': user.gender,  # Ensure gender exists in your user model
                    'role': role_name,  # Include the user's role
                    'token': request.session.session_key
                }

                return JsonResponse({'user': user_data}, status=200)
            else:
                return JsonResponse({'error': 'Invalid username or password.'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def user_logout(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            logout(request)  # Logs out the user
            return JsonResponse({'message': 'Logout successful.'}, status=200)
        else:
            return JsonResponse({'error': 'No user is logged in.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

# Add Hospital
@login_required
@csrf_exempt
def add_hospital(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        photo = request.FILES.get('photo')

        hospital = Hospital.objects.create(
            name=name,
            address=address,
            photo=photo
        )
        hospital.save()

        return JsonResponse({'message': 'Hospital added successfully.'}, status=201)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


#
@login_required
@require_POST
@csrf_exempt
def add_doctor(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))

        # Extract fields from the JSON data
        license_number = data.get('license_number')
        years_of_experience = data.get('years_of_experience')
        qualification = data.get('qualification')
        hospital_id = data.get('hospital_id')  # Ensure this matches the key in the JSON payload

        # Ensure all required fields are present
        if not all([license_number, years_of_experience, qualification, hospital_id]):
            return JsonResponse({'error': 'Missing required fields.'}, status=400)

        # Retrieve the hospital object
        hospital = get_object_or_404(Hospital, id=hospital_id)

        # Create the doctor record
        doctor = Doctor.objects.create(
            user=request.user,
            license_number=license_number,
            years_of_experience=years_of_experience,
            qualification=qualification,
            hospital=hospital
        )

        return JsonResponse({'message': 'Doctor added successfully.'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
@csrf_exempt
def add_appointment_slot(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))

        doctor_id = data.get('doctor')
        start_time = data.get('start_time')
        price = data.get('price')

        # Ensure required fields are provided
        if not doctor_id or not start_time or not price:
            return JsonResponse({'error': 'All fields are required.'}, status=400)

        # Fetch the doctor instance
        doctor = get_object_or_404(Doctor, id=doctor_id)

        # Create the appointment slot
        slot = AppointmentSlot.objects.create(
            doctor=doctor,
            start_time=start_time,
            price=price
        )

        return JsonResponse({'message': 'Appointment slot created successfully.'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
# Book Appointment

@login_required
@require_POST
@csrf_exempt
def book_appointment(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))

        slot_id = data.get('slot')

        if not slot_id:
            return JsonResponse({'error': 'Slot ID is required.'}, status=400)

        # Fetch the appointment slot instance
        slot = get_object_or_404(AppointmentSlot, id=slot_id)

        # Create the appointment
        appointment = Appointment.objects.create(
            appointment_slot=slot,
            user=request.user
        )

        return JsonResponse({'message': 'Appointment booked successfully.'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Add Prescription

@login_required
@require_POST
@csrf_exempt
def add_prescription(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))

        appointment_history_id = data.get('appointment_history')
        notes = data.get('notes')

        if not appointment_history_id or not notes:
            return JsonResponse({'error': 'Appointment history ID and notes are required.'}, status=400)

        # Fetch the appointment history instance
        appointment_history = get_object_or_404(AppointmentHistory, id=appointment_history_id)

        # Create the prescription
        prescription = Prescription.objects.create(
            appointment_history=appointment_history,
            notes=notes
        )

        return JsonResponse({'message': 'Prescription added successfully.'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Add Medication Prescription

@login_required
@require_POST
@csrf_exempt
def add_medication_prescription(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))

        prescription_id = data.get('prescription')
        medicine_id = data.get('medicine')
        dosage = data.get('dosage')
        frequency = data.get('frequency')
        when = data.get('when', [])

        if not prescription_id or not medicine_id or not dosage or not frequency:
            return JsonResponse({'error': 'Prescription ID, medicine ID, dosage, frequency, and when are required.'}, status=400)

        # Ensure 'when' is a list
        if not isinstance(when, list):
            return JsonResponse({'error': "'when' must be a list."}, status=400)

        prescription = get_object_or_404(Prescription, id=prescription_id)
        medicine = get_object_or_404(MedicationMaster, id=medicine_id)

        medication_prescription = MedicinePrescription.objects.create(
            prescription=prescription,
            medicine=medicine,
            dosage=dosage,
            frequency=frequency,
            when=when
        )
        medication_prescription.save()

        return JsonResponse({'message': 'Medication prescription added successfully.'}, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)