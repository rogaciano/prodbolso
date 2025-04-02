from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError

class NoNewUsersAccountAdapter(DefaultAccountAdapter):
    """
    Adapter que impede o cadastro de novos usuários.
    Apenas administradores podem criar contas através do admin.
    """
    def is_open_for_signup(self, request):
        """
        Indica se o site está aberto para cadastro.
        """
        return False  # Não permite cadastro público

    def pre_social_login(self, request, sociallogin):
        """
        Invocado quando um usuário tenta login social.
        """
        # Você pode personalizar o comportamento para login social aqui
        return super().pre_social_login(request, sociallogin)
