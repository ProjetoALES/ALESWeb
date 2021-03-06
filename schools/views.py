from django.shortcuts import render, get_object_or_404, HttpResponse, reverse
from .models import School, Student
from .forms import CityFormSet, SchoolFormSet, StudentFormSet, ChangeCoursesStudentForm, StudentInfo, YearFormSet, StudentForm
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.utils.datastructures import MultiValueDictKeyError
from main.decorators import *
from django.conf import settings
# Create your views here.


@user_passes_test(is_admin)
def update_city(request):
    """Update City
    Allows for the creation end edit of cities
    """

    if request.method == 'POST':
        form = CityFormSet(request.POST)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Cidades atualizadas!')

        else:
            return render(request, 'schools/update_cities.html', {'formset': form})

    form = CityFormSet()
    return render(request, 'schools/update_cities.html', {'formset': form})


@user_passes_test(is_admin)
def update_school(request):
    """Update School
    Allows for the creation and edit of schools
    """

    if request.method == 'POST':
        form = SchoolFormSet(request.POST)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Escolas atualizadas!')

        else:
            return render(request, 'schools/update_cities.html', {'formset': form})

    form = SchoolFormSet()
    return render(request, 'schools/update_schools.html', {'formset': form})


@user_passes_test(is_admin)
def update_year(request):
    """Update Year
    Allows for the creation and edit of years
    """

    if request.method == 'POST':
        form = YearFormSet(request.POST)

        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Séries atualizads!')

        else:
            return render(request, 'schools/update_years.html', {'formset': form})

    form = YearFormSet()
    return render(request, 'schools/update_years.html', {'formset': form})


@user_passes_test(is_admin)
def update_student(request, school_id):
    """Update Students
    Allows for the creation and edit of students
    Takes a school ID as URL parameter
    """

    if request.method == 'POST':
        form = StudentFormSet(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Alunos atualizados!')

        else:
            return render(request, 'schools/update_students.html', {'formset': form, 'school_id': school_id})

    form = StudentFormSet(queryset=School.objects.get(id=school_id).students.all())
    return render(request, 'schools/update_students.html', {'formset': form, 'school_id': school_id, 'school': School.objects.get(id=school_id).name})


@user_passes_test(is_teacher)
def quick_add_student(request):
    """Quick add student
    Allows for the quick creation of students
    """
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            url = form.apply_facebook(student)
            if url:
                url = settings.SITE_URL + reverse('custom_auth:confirm_facebook', kwargs={"key": url})
                messages.add_message(request, messages.SUCCESS, 'Dê esse link para x alunx se matricular:<br><span id="copy_url">{}</span>'.format(url))
            else:
                messages.add_message(request, messages.SUCCESS, 'Pronto! Adicione mais alunos abaixo')

        else:
            return render(request, 'schools/quick_add_student.html', {'form': form})

    form = StudentForm()
    form.fields['school'].queryset = request.user.teacher.schools
    return render(request, 'schools/quick_add_student.html', {'form': form})


@user_passes_test(is_teacher)
def student_update_auth(request):
    return render(request, 'schools/update_student_authorization.html')


@user_passes_test(is_teacher)
def student_update_submit(request):
    student = get_object_or_404(Student, id=request.POST['id'])

    try:
        status = request.POST['status']
        if status == 'true':
            student.is_authorized = True
        else:
            student.is_authorized = False
    except MultiValueDictKeyError:
        pass

    try:
        rg = request.POST['rg']
        student.document = rg
    except MultiValueDictKeyError:
        pass
    student.save()
    return HttpResponse()


@user_passes_test(is_teacher)
def student_search(request):
    name = request.POST['text']
    if name:
        students = Student.objects.filter(name__icontains=name).order_by('name')
    else:
        students = []
    results = []
    for student in students:
        entry = {
            'name': student.name,
            'year': student.year.name,
            'school': student.school.name,
            'id': student.pk,
            'status': student.is_authorized,
            'rg': '' if not student.document else student.document
        }
        results.append(entry)
    return JsonResponse({'students': results})


@user_passes_test(is_student)
def student_info(request):
    """Student Info
    Allows the student to change their info
    Visible at the Student Dashboard
    """

    if request.method == 'POST':
        form = StudentInfo(request.POST, instance=request.user.student)
        if form.is_valid():
            form.save()
            form.apply(request)
            messages.add_message(request, messages.SUCCESS, 'Informações atualizadas!')
    else:
        form = StudentInfo(instance=request.user.student)

    return render(request, 'schools/student_info.html', {'form': form})


@user_passes_test(is_student)
def change_courses(request):
    """Change Courses
    Allows for the changing of the enrolled courses
    """

    if request.method == 'POST':
        form = ChangeCoursesStudentForm(request.POST, instance=request.user.student)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Cursos atualizados!')
    else:
        form = ChangeCoursesStudentForm(instance=request.user.student)
    return render(request, 'schools/student_courses.html', {'form': form})
