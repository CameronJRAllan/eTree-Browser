import UI
import pytest
from unittest import TestCase

class TestUI(TestCase):
  def test_UI_initialization(self):
    try:
      UI.__init__('UI')
    except Exception as e:
      self.fail()

