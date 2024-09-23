from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Doctor, Patient, Appointment
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserForm, DoctorForm, PatientForm


def is_doctor(user):
    return hasattr(user, 'doctor')

def is_patient(user):
    return hasattr(user, 'patient')




def register_doctor(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        doctor_form = DoctorForm(request.POST)
        if user_form.is_valid() and doctor_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            login(request, user)
            return redirect('doctor_dashboard')
    else:
        user_form = UserForm()
        doctor_form = DoctorForm()
    return render(request, 'appointments/register_doctor.html', {'user_form': user_form, 'doctor_form': doctor_form})

def register_patient(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        patient_form = PatientForm(request.POST)
        if user_form.is_valid() and patient_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            patient = patient_form.save(commit=False)
            patient.user = user
            patient.save()
            login(request, user)
            return redirect('patient_dashboard')
    else:
        user_form = UserForm()
        patient_form = PatientForm()
    return render(request, 'appointments/register_patient.html', {'user_form': user_form, 'patient_form': patient_form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if hasattr(user, 'doctor'):
                return redirect('doctor_dashboard')
            elif hasattr(user, 'patient'):
                return redirect('patient_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'appointments/login.html', {'form': form})






@login_required
@user_passes_test(is_doctor)
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = doctor.appointments.all()
    return render(request, 'appointments/doctor_dashboard.html', {'doctor': doctor, 'appointments': appointments})

@login_required
@user_passes_test(is_patient)
def patient_dashboard(request):
    patient = get_object_or_404(Patient, user=request.user)
    appointments = patient.appointments.all()
    doctors = Doctor.objects.all()  
    return render(request, 'appointments/patient_dashboard.html', {
        'patient': patient,
        'appointments': appointments,
        'doctors': doctors
    })

@login_required
@user_passes_test(is_patient)
def book_appointment(request, doctor_id):
    patient = get_object_or_404(Patient, user=request.user)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if request.method == 'POST':
        appointment_date = request.POST.get('appointment_date')
        reason = request.POST.get('reason')
        Appointment.objects.create(doctor=doctor, patient=patient, appointment_date=appointment_date, reason=reason)
        return redirect('patient_dashboard')  
    return render(request, 'appointments/book_appointment.html', {'doctor': doctor})
