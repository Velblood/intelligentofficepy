import unittest
from datetime import datetime
from unittest.mock import patch, Mock, PropertyMock

import mock.GPIO as GPIO
from mock.SDL_DS3231 import SDL_DS3231
from mock.adafruit_veml7700 import VEML7700
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

    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    def test_check_manage_light_off(self, mock_lux: Mock):
        mock_lux.return_value = 500
        io = IntelligentOffice()
        io.manage_light_level()
        self.assertFalse(io.light_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    def test_check_manage_light_on_if_not_enough(self, mock_lux: Mock, mock_occupancy: Mock, mock_light: Mock):
        mock_lux.return_value = 499
        mock_occupancy.return_value = True
        io = IntelligentOffice()
        io.manage_light_level()
        mock_light.assert_called_with(io.LED_PIN, True)
        self.assertTrue(io.light_on)

    @patch.object(GPIO, "output")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    def test_check_manage_light_off_if_enough(self, mock_lux: Mock, mock_light: Mock):
        mock_lux.return_value = 551
        io = IntelligentOffice()
        io.light_on = True
        io.manage_light_level()
        mock_light.assert_called_with(io.LED_PIN, False)
        self.assertFalse(io.light_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    def test_check_manage_light_on_if_someone_enter(self, mock_lux: Mock, mock_occupancy: Mock, mock_light: Mock):
        mock_occupancy.return_value = True
        mock_lux.return_value = 480
        io = IntelligentOffice()
        io.manage_light_level()
        mock_light.assert_called_with(io.LED_PIN, True)
        self.assertTrue(io.light_on)

    @patch.object(GPIO, "input")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    def test_check_manage_light_of_if_nobody_in(self, mock_lux: Mock, mock_occupancy: Mock):
        mock_occupancy.return_value = False
        mock_lux.return_value = 480
        io = IntelligentOffice()
        io.manage_light_level()
        self.assertFalse(io.light_on)

    @patch.object(GPIO, "input")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    def test_check_manage_light_on_if_nobody_left(self, mock_lux: Mock, mock_occupancy: Mock):
        mock_occupancy.return_value = True
        mock_lux.return_value = 480
        io = IntelligentOffice()
        io.manage_light_level()
        self.assertTrue(io.light_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    @patch.object(VEML7700, "lux", new_callable=PropertyMock)
    def test_check_manage_light_on_if_all_left(self, mock_lux: Mock, mock_occupancy: Mock, mock_light: Mock):
        mock_occupancy.return_value = False
        mock_lux.return_value = 520
        io = IntelligentOffice()
        io.manage_light_level()
        mock_light.assert_called_with(io.LED_PIN, False)
        self.assertFalse(io.light_on)

    @patch.object(GPIO, "input")
    def test_check_monitor_buzzer_off(self, mock_sensor: Mock):
        mock_sensor.return_value = False
        io = IntelligentOffice()
        io.monitor_air_quality()
        self.assertFalse(io.buzzer_on)

    @patch.object(GPIO, "output")
    @patch.object(GPIO, "input")
    def test_check_monitor_buzzer_on(self, mock_sensor: Mock, mock_buzzer: Mock):
        mock_sensor.return_value = True
        io = IntelligentOffice()
        io.monitor_air_quality()
        mock_buzzer.assert_called_with(io.BUZZER_PIN, True)
        self.assertTrue(io.buzzer_on)
