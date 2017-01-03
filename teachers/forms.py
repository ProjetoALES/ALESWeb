from django import forms
from .models import Teacher
from courses.models import Course
import phonenumbers


class TeacherForm(forms.ModelForm):
    """TeacherForm
    Base form for the creation and editing of teachers
    """

    class Meta:
        model = Teacher
        fields = ['name', 'nickname', 'email', 'phone', 'schools']
        labels = {
            'name': 'Nome',
            'nickname': 'Apelido',
            'phone': 'Telefone',
            'schools': 'Escolas',
        }

        widgets = {
            'schools': forms.widgets.CheckboxSelectMultiple(),
        }

    def clean_phone(self):
        # Only allows valid phones
        data = self.cleaned_data.get('phone', '')
        if not data:
            raise forms.ValidationError("Telefone necessário")
        try:
            x = phonenumbers.parse(data, 'BR')
            data = phonenumbers.format_number(x, 'BR')
        except:
            raise forms.ValidationError(
                "Número de telefone inválido"
            )
        return data


# TeacherFormSet for the creation and editing of teacher
TeacherFormSet = forms.modelformset_factory(Teacher, form=TeacherForm, can_delete=True)


class ChangeCoursesTeacherForm(forms.ModelForm):
    """ChangeCoursesTeacherForm
    Allows for the change of courses
    """

    class Meta:
        model = Teacher
        fields = ['courses']
        widgets = {
            'courses': forms.widgets.CheckboxSelectMultiple(),
        }

    # Representing the many to many related field in Teacher
    courses = forms.ModelMultipleChoiceField(queryset=Course.objects.all())

    # Overriding __init__ here allows us to provide initial
    # data for 'courses' field
    def __init__(self, *args, **kwargs):
        super(ChangeCoursesTeacherForm, self).__init__(*args, **kwargs)

        self.fields['courses'].queryset = Course.objects.filter(schools__in=self.instance.schools.all()).distinct()
        # The widget for a ModelMultipleChoiceField expects
        # a list of primary key for the selected data.
        self.initial['courses'] = [t.pk for t in self.instance.courses.all()]

        # forms.ModelForm.__init__(self, *args, **kwargs)

    # Overriding save allows us to process the value of 'courses' field
    def save(self, commit=True):
        # Get the unsaved instance
        instance = forms.ModelForm.save(self, False)

        # Prepare a 'save_m2m' method for the form,
        old_save_m2m = self.save_m2m

        def save_m2m():
            old_save_m2m()
            # This is where we actually link the courses
            instance.courses.clear()
            for course in self.cleaned_data['courses']:
                instance.courses.add(course)
        self.save_m2m = save_m2m

        # Do we need to save all changes now?
        if commit:
            instance.save()
            self.save_m2m()

        return instance