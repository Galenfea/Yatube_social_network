from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User_ = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User_
        fields = ('first_name', 'last_name', 'username', 'email')
