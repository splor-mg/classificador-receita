"""Testes de validação de salto de nível e zeros canônicos intermédios."""

from django.test import SimpleTestCase

from apps.core.parent_item_validation import (
    intermediate_levels_canonical_zero_error_message,
)


class IntermediateCanonicalZeroMessageTests(SimpleTestCase):
    def test_message_uses_child_and_parent_level_numbers(self):
        msg = intermediate_levels_canonical_zero_error_message(7, 5)
        self.assertIn("nível 7", msg)
        self.assertIn("nível 5", msg)
        self.assertIn("zeros canônicos", msg)
