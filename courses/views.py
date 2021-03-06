from django.shortcuts import render, reverse, redirect
from .models import Event, Course
from schools.models import Student
from teachers.models import Teacher
from .forms import CourseFormSet, EventForm, StudentPresence, EventFormSet
from django.db.models import Q
from django.forms import formset_factory
from django.contrib.auth.decorators import user_passes_test
from main.decorators import *
from django.contrib import messages
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
# Create your views here.


def course_view(request, course_slug):
    print(course_slug)
    course = get_object_or_404(Course, slug=course_slug)
    return render(request, 'courses/course_view.html', {'course': course})


def event_view(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    return render(request, 'courses/event_view.html', {'event': event})


@user_passes_test(is_admin)
def update_course(request):
    """Update Course
    Admin only
    Allows for the creation end edit of courses
    """

    if request.method == 'POST':
        # gather post data into form
        form = CourseFormSet(request.POST)

        # If the form is valid, save the changes and render message
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Cursos atualizados!')

        # If the form is invalid, reload page with form errors
        else:
            return render(request, 'schools/update_courses.html', {'formset': form})

    # If GET, generate an unmodified form
    form = CourseFormSet(queryset=Course.objects.order_by('city', 'time'))
    for course in form:
        course.fields['teachers'].queryset = Teacher.objects.filter(cities__in=[course.instance.city])
        course.fields['coordinators'].queryset = Teacher.objects.filter(Q(courses__in=[course.instance]) | Q(coordinated_courses__in=[course.instance])).distinct()
    return render(request, 'schools/update_courses.html', {'formset': form})


@user_passes_test(is_teacher)
def create_event(request):
    """Create event
    Teacher only
    Allows for the creation of events
    """

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EventForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # Save the form and recover the new event object
            new = form.save()
            # set the event teacher as the current teacher
            new.teacher = request.user.teacher
            # save the changes and render success message
            new.save()
            messages.add_message(request, messages.SUCCESS, 'Evento adicionado!')
            # create new empty form
            form = EventForm()

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EventForm()

    # Teachers can only select certain courses(the ones they are enrolled in)
    form.fields["course"].queryset = request.user.teacher.courses.all()

    return render(request, 'teachers/create_event.html', {'form': form})


@user_passes_test(is_teacher)
def update_event(request):
    """Update event
    Teacher only
    Allows for the editing and deletion of the teacher's events
    """

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EventFormSet(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # and save it
            form.save()

            all_instances = [i.instance for i in form]
            deleted = [i.instance for i in form.deleted_forms]

            # Save manually so pre_save is triggered
            for item in all_instances:
                if item not in deleted:
                    item.save()

            messages.add_message(request, messages.SUCCESS, 'Eventos atualizados!')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EventFormSet(queryset=request.user.teacher.events.filter(datetime__gte=timezone.now() - timedelta(hours=3)).order_by('-datetime'))
    # for every form in the formset
    for item in form:
        # Teachers can only select certain courses(the ones they are enrolled in)
        item.fields["course"].queryset = request.user.teacher.courses.all()

    return render(request, 'teachers/update_events.html', {'formset': form})


@user_passes_test(is_teacher)
def presence_list(request, event_id):
    """Presence list
    Teacher only
    Allows for the editing of the presence list of a given event
    """
    # Get the event(if it does not exist, the website will break but that's ok)
    event = Event.objects.get(id=event_id)

    # if the event does not belong to the current teacher, render the index page
    if not request.user.teacher.courses.filter(id=event.course.id).exists():
        return redirect('index')

    # Create a new formset with the right size
    PresenceFormSet = formset_factory(StudentPresence, extra=0)

    def new_form():
        current_list = []

        # Students that are present
        present_students = event.students_attended.all()

        # Set all of the forms values to those of every student
        for student in event.students.order_by('name'):
            values = {
                'name': student.name,
                'year': student.year.name,
                'school': student.school.name,
                'presence': False,
                'id': student.id,
                'is_authorized': student.is_authorized
            }
            # And set the presence as True for the students that are present
            if student in present_students:
                values['presence'] = True
            current_list.append(values)

        # set the initial values
        form = PresenceFormSet(initial=current_list)
        return form

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = PresenceFormSet(request.POST)

        # check whether it's valid:
        if form.is_valid():

            # For every form in the formset
            for item in form:

                # if the form is not empty
                if item['id'].value():
                    # apply the changes to the students' presences
                    update_presence(item['id'].value(), event.id, item['presence'].value())

            # success message
            messages.add_message(request, messages.SUCCESS, 'Lista de presença atualizada!')
            form = new_form()

    # if a GET (or any other method) we'll create a blank form
    else:
        form = new_form()

    # Pass the event object to render some nice info
    return render(request, 'teachers/presence_list.html', {'formset': form, 'event': event})


def update_presence(student_id, event_id, value):
    # Little helper that applies the changes
    # Takes the student and event ids and the value

    student = Student.objects.get(id=student_id)
    event = Event.objects.get(id=event_id)

    # Update the event's fields
    if value:
        student.events_attended.add(event)
        student.events_missed.remove(event)
    else:
        student.events_attended.remove(event)
        student.events_missed.add(event)
