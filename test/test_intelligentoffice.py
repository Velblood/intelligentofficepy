import unittest
from datetime import datetime
from unittest.mock import patch, Mock

import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
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

    @patch.object(SDL_DS3231, "read_datetime")
    def test_check_blinds_closed(self, mock_datetime: Mock):
        mock_datetime.return_value = datetime(2024, 11, 27, 7, 59, 59, 59)
        io = IntelligentOffice()
        io.manage_blinds_based_on_time()
        self.assertFalse(io.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_check_blinds_opened_in_normal_day(self, mock_datetime: Mock, mock_servo: Mock):
        mock_datetime.return_value = datetime(2024, 11, 27, 8, 0, 0)
        io = IntelligentOffice()
        io.manage_blinds_based_on_time()
        mock_servo.assert_called_with(12)
        self.assertTrue(io.blinds_open)

    @patch.object(IntelligentOffice, "change_servo_angle")
    @patch.object(SDL_DS3231, "read_datetime")
    def test_check_blinds_closed_evening_in_normal_day(self, mock_datetime: Mock, mock_servo: Mock):
        mock_datetime.return_value = datetime(2024, 11, 27, 20, 0, 0)
        io = IntelligentOffice()
        io.manage_blinds_based_on_time()
        mock_servo.assert_called_with(2)
        self.assertFalse(io.blinds_open)

    @patch.object(SDL_DS3231, "read_datetime")
    def test_check_blinds_closed_weekend(self, mock_datetime: Mock):
        mock_datetime.return_value = datetime(2024, 11, 30, 20, 0, 0)
        io = IntelligentOffice()
        io.manage_blinds_based_on_time()
        self.assertFalse(io.blinds_open)
