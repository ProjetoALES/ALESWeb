from django.shortcuts import render, get_object_or_404, redirect, reverse
from .forms import TeacherFormSet, TeacherForm, ChangeCoursesTeacherForm, TeacherInfo, EmailListForm
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from main.decorators import *
from courses.models import Event, Course
from courses.forms import CourseForm
from project.manual_error_report import exception_email
from django.db.models import Q
from teachers.models import EmailList, Teacher
from django.conf import settings
from django.http import Http404, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from main.email_helpers import generic_message
from django.utils import timezone
from django import forms
import time
import sys
from smtplib import SMTPSenderRefused
# Create your views here.


@user_passes_test(is_admin)
def update_teacher(request):
    """Update Teacher
    Allows the Admin to add and update teachers' information, except passwords.
    Generates a FormSet with all the teachers' infos
    """

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TeacherFormSet(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # Aplly it
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Professores atualizados!')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TeacherFormSet()

    return render(request, 'teachers/update_teachers.html', {'formset': form})


@user_passes_test(is_teacher)
def update_info(request):
    """Update Info - Teacher
    Allows Teachers to update their info
    Shows on Teacher Dashboard
    """

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TeacherInfo(request.POST, instance=request.user.teacher)
        # check whether it's valid:
        if form.is_valid():
            form.save()
            form.apply(request)
            messages.add_message(request, messages.SUCCESS, 'Informações atualizadas!')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = TeacherInfo(instance=request.user.teacher)

    return render(request, 'teachers/teacher_info.html', {'form': form})


@user_passes_test(is_teacher)
def change_courses(request):
    """Change Courses - Teacher
    Allows Teachers to change their enrolled courses
    Shows on Teacher Dashboard
    """

    if request.method == 'POST':
        form = ChangeCoursesTeacherForm(request.POST, instance=request.user.teacher)
        print(form)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Cursos atualizados!')
    else:
        form = ChangeCoursesTeacherForm(instance=request.user.teacher)
        res = request.user.teacher.cities.all()[0].courses.all()
        for city in request.user.teacher.cities.all()[1:]:
            res = res | city.courses.all()
        form.fields["courses"].queryset = res.order_by('name')

    return render(request, 'teachers/teacher_courses.html', {'form': form})


@user_passes_test(is_teacher)
def coordinate_courses(request):
    """Coordinate Courses
    Teacher only
    Allows for the coordination of courses
    """
    CourseFormSet = forms.modelformset_factory(Course, form=CourseForm, can_delete=False, extra=0)

    if request.method == 'POST':
        # gather post data into form
        form = CourseFormSet(request.POST)

        # If the form is valid, save the changes and render message
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Cursos atualizados!')

        # If the form is invalid, reload page with form errors
        else:
            return render(request, 'teachers/update_coordinated_courses.html', {'formset': form})

    # If GET, generate an unmodified form
    form = CourseFormSet(queryset=request.user.teacher.coordinated_courses.all())
    for course in form:
        course.fields['teachers'].queryset = Teacher.objects.filter(cities__in=[course.instance.city])
        course.fields['coordinators'].queryset = Teacher.objects.filter(Q(courses__in=[course.instance]) | Q(coordinated_courses__in=[course.instance])).distinct()
    return render(request, 'teachers/update_coordinated_courses.html', {'formset': form})


def download_presence(request, event_id):
    """Download Presence

    returns the presence list for a given event in PDF form
    """
    event = get_object_or_404(Event, id=event_id)

    fevent = []
    for student in event.students.order_by('name'):
        status = False
        if student in event.students_attended.all():
            status = True
        fevent.append(
            {
                'name': student.name,
                'year': student.year,
                'school': student.school.name,
                'status': status
            }
        )

    return render(request, 'teachers/pdf_presence.html', {'fevent': fevent, 'event': event})


@user_passes_test(is_teacher)
def email_lists(request):
    """List of Email Lists

    returns a list of created email lists and allows the teacher to send them
    """

    return render(request, 'teachers/email_lists.html', {'emails': request.user.teacher.email_lists.all().order_by('-created')})


@user_passes_test(is_teacher)
def create_email_list(request):
    """Create email lists view
    """

    if request.method == 'POST':
        form = EmailListForm(request.POST)
        if form.is_valid():
            new = form.save()

            new.teacher = request.user.teacher

            new.save()
            messages.add_message(request, messages.SUCCESS, 'Lista Criada!')
            form = EmailListForm()
            return redirect('email-lists')
    else:
        form = EmailListForm()

    form.fields["courses"].queryset = request.user.teacher.courses.all()

    return render(request, 'teachers/create_email_list.html', {'form': form})


@user_passes_test(is_teacher)
def edit_email_list(request, email_id):
    """Create email lists view
    """
    instance = get_object_or_404(EmailList, id=email_id)

    if instance not in request.user.teacher.email_lists.all():
        raise Http404

    if request.method == 'POST':
        form = EmailListForm(request.POST, instance=instance)
        if form.is_valid():
            new = form.save()

            new.teacher = request.user.teacher

            new.save()
            messages.add_message(request, messages.SUCCESS, 'Lista editada!')
            form = EmailListForm(instance=instance)
            return redirect("email-lists")
    else:
        form = EmailListForm(instance=instance)

    form.fields["courses"].queryset = request.user.teacher.courses.all()

    return render(request, 'teachers/edit_email_list.html', {'form': form, 'id': email_id})


@user_passes_test(is_teacher)
def delete_email_list(request, email_id):
    """Create email lists view
    """
    instance = get_object_or_404(EmailList, id=email_id)

    if instance not in request.user.teacher.email_lists.all():
        raise Http404

    instance.delete()
    messages.add_message(request, messages.SUCCESS, "Lista apagada")

    return redirect('email-lists')


@user_passes_test(is_teacher)
def preview_email_list(request):
    """Preview email list
    """
    try:
        email_id = request.POST['email_id']
    except MultiValueDictKeyError:
        email_id = None

    if email_id:
        instance = get_object_or_404(EmailList, id=email_id)
    else:
        instance = EmailList(
            title=request.POST['title'],
            subject=request.POST['subject'],
            message=request.POST['message'],
            theme=request.POST['theme'],
            teacher=request.user.teacher,
            greeting=request.POST['greeting'],
            html=True if request.POST['html'] == 'true' else False
        )

    instance.message = instance.message.replace('$$nome$$', "NOME DO ALUNO")
    instance.message = instance.message.replace('$$curso$$', "NOME DO CURSO")
    instance.title = instance.title.replace('$$nome$$', "NOME DO ALUNO")
    instance.title = instance.title.replace('$$curso$$', "NOME DO CURSO")

    context = {
        'instance': instance,
        'project_url': settings.SITE_URL
    }

    return render(request, 'main/email/generic_message.html', context)


@user_passes_test(is_teacher)
def send_email_list(request, email_id):
    """Send email list
    """
    instance = get_object_or_404(EmailList, id=email_id)
    sent = 0
    total = instance.total_to_be_sent
    t1 = time.time()
    try:
        sent = int(request.POST['sent'])

        if instance not in request.user.teacher.email_lists.all():
            raise Http404

        sent, total = generic_message(instance, sent)

        instance.sent = timezone.localtime(timezone.now())
        instance.save()

        msg = "{}% concluído".format(round(sent / total * 100, 1))
    except SMTPSenderRefused:
        # Sleep for some seconds to avoid flooding the server
        time.sleep(abs(26 - (time.time() - t1)))
        msg = "Reconectando..."
    except Exception as e:
        # Sleep for some seconds to avoid flooding the server
        time.sleep(abs(26 - (time.time() - t1)))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        msg = "Oops! Reporte isso para o adm: " + str([exc_type, exc_obj])
        try:
            exception_email(request, e)
        except Exception as ee:
            pass

    return JsonResponse({'sent': sent, 'total': total, 'msg': msg})


@user_passes_test(is_admin)
def quick_add_teacher(request):
    """Quick add student
    Allows for the quick creation of students
    """
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            student = form.save()
            url = form.apply_facebook(student)
            if url:
                url = settings.SITE_URL + reverse('custom_auth:confirm_facebook', kwargs={"key": url})
                messages.add_message(request, messages.SUCCESS, 'Dê esse link para x professorx se matricular:<br><span id="copy_url">{}</span>'.format(url))
            else:
                messages.add_message(request, messages.SUCCESS, 'Pronto! Adicione mais professores abaixo')

        else:
            return render(request, 'teachers/quick_add_teacher.html', {'form': form})

    form = TeacherForm()
    return render(request, 'teachers/quick_add_teacher.html', {'form': form})
