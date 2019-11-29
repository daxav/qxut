import functools
import gzip
import re
from difflib import SequenceMatcher
from pathlib import Path

from django.conf import settings
from django.core.exceptions import (
    FieldDoesNotExist, ImproperlyConfigured, ValidationError,
)
from django.utils.functional import lazy
from django.utils.html import format_html, format_html_join
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _, ngettext
from django.contrib.auth.password_validation import CommonPasswordValidator

class TranslatedMinimumLengthValidator:
    """
    Validate whether the password is of a minimum length.
    """
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "Senha muito curta. Deve ter no mínimo %(min_length)d caractere.",
                    "Senha muito curta. Deve ter no mínimo %(min_length)d caracteres.",
                    self.min_length
                ),
                code='password_too_short',
                params={'min_length': self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            "Sua senha deve conter no mínimo %(min_length)d caractere.",
            "Sua senha deve conter no mínimo %(min_length)d caractere.",
            self.min_length
        ) % {'min_length': self.min_length}


class TranslatedUserAttributeSimilarityValidator:
    """
    Validate whether the password is sufficiently different from the user's
    attributes.
    If no specific attributes are provided, look at a sensible list of
    defaults. Attributes that don't exist are ignored. Comparison is made to
    not only the full attribute value, but also its components, so that, for
    example, a password is validated against either part of an email address,
    as well as the full address.
    """
    DEFAULT_USER_ATTRIBUTES = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, user_attributes=DEFAULT_USER_ATTRIBUTES, max_similarity=0.7):
        self.user_attributes = user_attributes
        self.max_similarity = max_similarity

    def validate(self, password, user=None):
        if not user:
            return

        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_parts = re.split(r'\W+', value) + [value]
            for value_part in value_parts:
                if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:
                    try:
                        verbose_name = str(user._meta.get_field(attribute_name).verbose_name)
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        _("A senha é muito similiar ao %(verbose_name)s."),
                        code='password_too_similar',
                        params={'verbose_name': verbose_name},
                    )

    def get_help_text(self):
        return _('Sua senha não pode ser muito similar às suas outras informações pessoais.')


class TranslatedCommonPasswordValidator(CommonPasswordValidator):

    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("Essa senha é muito comum."),
                code='password_too_common',
            )

    def get_help_text(self):
        return _('Sua senha não pode ser muito comum.')


class TranslatedNumericPasswordValidator:
    """
    Validate whether the password is alphanumeric.
    """
    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("Essa senha é totalmente numérica."),
                code='password_entirely_numeric',
            )

    def get_help_text(self):
        return _('Sua senha não pode conter somente números.')