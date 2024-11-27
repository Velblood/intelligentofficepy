import unittest
from unittest.mock import patch, Mock

import mock.GPIO as GPIO
from src.intelligentoffice import IntelligentOffice, IntelligentOfficeError


class TestIntelligentOffice(unittest.TestCase):

    def test_check_quadrant_occupancy_wrong_pin_low(self):
        io = IntelligentOffice()
        self.assertRaises(IntelligentOfficeError, io.check_quadrant_occupancy, 10)

    def test_check_quadrant_occupancy_wrong_pin_between(self):
        io = IntelligentOffice()
        self.assertRaises(IntelligentOfficeError, io.check_quadrant_occupancy, 14)

    def test_check_quadrant_occupancy_wrong_pin_high(self):
        io = IntelligentOffice()
        self.assertRaises(IntelligentOfficeError, io.check_quadrant_occupancy, 16)

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_true(self, mock_object: Mock):
        mock_object.return_value = True
        io = IntelligentOffice()
        self.assertTrue(io.check_quadrant_occupancy(io.INFRARED_PIN1))

    @patch.object(GPIO, "input")
    def test_check_quadrant_occupancy_false(self, mock_object: Mock):
        mock_object.return_value = False
        io = IntelligentOffice()
        self.assertFalse(io.check_quadrant_occupancy(io.INFRARED_PIN3))
