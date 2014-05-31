import unittest as ut
import ctp

class Test_is_keyword(ut.TestCase):
    def test_valids(self):
        self.assertTrue(ctp._is_keyword('check'))
        self.assertTrue(ctp._is_keyword('set'))
        self.assertTrue(ctp._is_keyword('vin'))
        self.assertTrue(ctp._is_keyword('delay'))
        self.assertTrue(ctp._is_keyword('rest'))

    def test_invalids(self):
        self.assertFalse(ctp._is_keyword(10))
        self.assertFalse(ctp._is_keyword(10.2))
        self.assertFalse(ctp._is_keyword('habla'))
        self.assertFalse(ctp._is_keyword(['vin', 'check']))
        self.assertFalse(ctp._is_keyword(['check', 'vin']))
        self.assertFalse(ctp._is_keyword(['check', 'set']))

class Test_is_pin(ut.TestCase):
    def test_valids(self):
        self.assertTrue(ctp._is_pin('1'))
        self.assertTrue(ctp._is_pin('2'))
        self.assertTrue(ctp._is_pin('3'))
        self.assertTrue(ctp._is_pin('4'))
        self.assertTrue(ctp._is_pin('5'))
        self.assertTrue(ctp._is_pin('6'))
        self.assertTrue(ctp._is_pin('7'))
        self.assertTrue(ctp._is_pin('8'))
        self.assertTrue(ctp._is_pin('9'))
        self.assertTrue(ctp._is_pin('10'))
        self.assertTrue(ctp._is_pin('11'))
        self.assertTrue(ctp._is_pin('12'))
        self.assertTrue(ctp._is_pin('13'))
        self.assertTrue(ctp._is_pin('14'))
        self.assertTrue(ctp._is_pin('15'))
        self.assertTrue(ctp._is_pin('16'))

    def test_invalids(self):
        self.assertFalse(ctp._is_pin('0'))
        self.assertFalse(ctp._is_pin('17'))
        self.assertFalse(ctp._is_pin('-1'))     
        self.assertFalse(ctp._is_pin('habla'))

class Test_pins_to_arg(ut.TestCase):
    def test_valids(self):
        case = {
            1:True, 2:True, 3:True, 4:True, 
            5:True, 6:True, 7:True, 8:True,
            9:True, 10:True, 11:True, 12:True, 
            13:True, 14:True, 15:True, 16:True
        }
        self.assertEqual(ctp._pins_to_arg(case),0b1111111111111111)
        self.assertNotEqual(ctp._pins_to_arg(case),0b11111111111111110)

        case = {
            1:False, 2:False, 3:False, 4:False, 
            5:True, 6:True, 7:True, 8:True,
            9:False, 10:False, 11:False, 12:False, 
            13:True, 14:True, 15:True, 16:True
        }
        self.assertEqual(ctp._pins_to_arg(case),0b1111000011110000)
        self.assertNotEqual(ctp._pins_to_arg(case),0b11110000111100001)

        case = {
            1:True, 2:True, 3:True, 4:True
        }
        self.assertEqual(ctp._pins_to_arg(case),0b1111)
        self.assertNotEqual(ctp._pins_to_arg(case),0b11110)

    def test_invalids(self):
        case = [ True, True, True, True, False ]
        self.assertRaises(TypeError,ctp._pins_to_arg, case)            

class Test_get_pin_vals(ut.TestCase):
    def test_valids(self):
        case = 'on 1 2'
        self.assertEqual(ctp._get_pin_vals(case.split()), {1: True, 2: True})
        self.assertTrue(len(ctp._get_pin_vals(case.split())) == 2)

        case = 'off 1 2'
        self.assertEqual(ctp._get_pin_vals(case.split()), 
            {1: False, 2: False})
        self.assertTrue(len(ctp._get_pin_vals(case.split())) == 2)

        case = 'on 1 2 off 3 4'
        self.assertEqual(ctp._get_pin_vals(case.split()), 
            {1: True, 2: True, 3: False, 4: False})
        self.assertTrue(len(ctp._get_pin_vals(case.split())) == 4)

    def test_rest_keyword(self):
        case = 'on 1 2 off rest'
        self.assertEqual(ctp._get_pin_vals(case.split()), 
            {
                1: True, 2: True, 3: False, 4: False, 
                5: False, 6: False, 7: False, 8: False,
                9: False, 10: False, 11: False, 12: False,
                13: False, 14: False, 15: False, 16: False
            })
        self.assertTrue(len(ctp._get_pin_vals(case.split())) == 16)
        
        case = 'off 1 2 on rest'
        self.assertEqual(ctp._get_pin_vals(case.split()), 
            {
                1: False, 2: False, 3: True, 4: True, 
                5: True, 6: True, 7: True, 8: True,
                9: True, 10: True, 11: True, 12: True,
                13: True, 14: True, 15: True, 16: True,
            })
        self.assertTrue(len(ctp._get_pin_vals(case.split())) == 16)

        case = 'on rest'
        self.assertEqual(ctp._get_pin_vals(case.split()), 
            {
                1: True, 2: True, 3: True, 4: True, 
                5: True, 6: True, 7: True, 8: True,
                9: True, 10: True, 11: True, 12: True,
                13: True, 14: True, 15: True, 16: True,
            })
        self.assertTrue(len(ctp._get_pin_vals(case.split())) == 16)

        case = 'off rest'
        self.assertEqual(ctp._get_pin_vals(case.split()), 
            {
                1: False, 2: False, 3: False, 4: False, 
                5: False, 6: False, 7: False, 8: False,
                9: False, 10: False, 11: False, 12: False,
                13: False, 14: False, 15: False, 16: False
            })
        self.assertTrue(len(ctp._get_pin_vals(case.split())) == 16)

    def test_invalids(self):
        case = 'habla 1'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "'habla' is not a valid pin or value", ctp._get_pin_vals, case)
        case = 'habla'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "'habla' is not a valid pin or value", ctp._get_pin_vals, case)
        case = 'on habla'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "'habla' is not a valid pin or value", ctp._get_pin_vals, case)
        case = 'on 1, 2'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "'1,' is not a valid pin or value", ctp._get_pin_vals, case)

    def test_no_value_given(self):
        case = '1'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "pins must be preceded by either ON or OFF", 
            ctp._get_pin_vals, case)
        case = 'rest'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "pins must be preceded by either ON or OFF", 
            ctp._get_pin_vals, case)

    def test_rest_not_last(self):
        case = 'on rest 2'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "REST keyword must be the last argument", ctp._get_pin_vals, case)
        case = 'on rest off 1'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "REST keyword must be the last argument", ctp._get_pin_vals, case)

    def test_mult_values(self):
        case = 'on 1 1'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "pin 1 has already been given a value", ctp._get_pin_vals, case)
        case = 'on 1 off 1'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "pin 1 has already been given a value", ctp._get_pin_vals, case)

class Test_cmd_check(ut.TestCase):
    def test_valids(self):
        case = 'on 1 2 off rest'.split()
        self.assertEqual(ctp._cmd_check(case), b'\x01\x03\x00')
        case = 'on rest'.split()
        self.assertEqual(ctp._cmd_check(case), b'\x01\xff\xff')

    def test_invalids(self):
        case = 'on 1 2'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError, 
            "all pins must be given a value", ctp._cmd_check, case)

class Test_cmd_set(ut.TestCase):
    def test_valids(self):
        case = 'on 1 2 off rest'.split()
        self.assertEqual(ctp._cmd_set(case), b'\x02\x03\x00')
        
        case = 'off rest'.split()
        ctp._cmd_set(case)
        case = 'on 3 1'.split()
        self.assertEqual(ctp._cmd_set(case), b'\x02\x05\x00')

        case = 'on rest'.split()
        ctp._cmd_set(case)
        case = 'off 3 1'.split()
        self.assertEqual(ctp._cmd_set(case), b'\x02\xfa\xff')

class Test_cmd_vin(ut.TestCase):
    def test_valids(self):
        case = '5 14 15 16'.split()
        self.assertEqual(ctp._cmd_vin(case), b'\x03\x10\xe0')
        case = '16'.split()
        self.assertEqual(ctp._cmd_vin(case), b'\x03\x00\x80')

    def test_invalid_pins(self):
        case = '1 2'
        self.assertRaisesRegex(ctp.CtpSyntaxError, "Invalid vin pin",
            ctp._cmd_vin, case)
        case = '17'
        self.assertRaisesRegex(ctp.CtpSyntaxError, "Invalid vin pin",
            ctp._cmd_vin, case)
        case = 'habla'
        self.assertRaisesRegex(ctp.CtpSyntaxError, "Invalid vin pin",
            ctp._cmd_vin, case)

class Test_cmd_gnd(ut.TestCase):
    def test_valids(self):
        case = '8 12'.split()
        self.assertEqual(ctp._cmd_gnd(case), b'\x04\x80\x08')
        case = '12'.split()
        self.assertEqual(ctp._cmd_gnd(case), b'\x04\x00\x08')

    def test_invalid_pins(self):
        case = '1 2'
        self.assertRaisesRegex(ctp.CtpSyntaxError, "Invalid ground pin", 
            ctp._cmd_gnd, case)
        case = '17'
        self.assertRaisesRegex(ctp.CtpSyntaxError, "Invalid ground pin", 
            ctp._cmd_gnd, case)
        case = 'habla'
        self.assertRaisesRegex(ctp.CtpSyntaxError, "Invalid ground pin", 
            ctp._cmd_gnd, case)

class Test_cmd_delay(ut.TestCase):
    def test_valids(self):
        case = '100'.split()
        self.assertEqual(ctp._cmd_delay(case), b'\x05\x64\x00')
        case = '0'.split()
        self.assertEqual(ctp._cmd_delay(case), b'\x05\x00\x00')
        case = '65535'.split()
        self.assertEqual(ctp._cmd_delay(case), b'\x05\xff\xff')

    def test_invalids(self):
        case = 'habla'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError,
            'delay time must be a number', ctp._cmd_delay, case)
        case = '100 100'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError,
            'only 1 delay value can be specified', ctp._cmd_delay, case)
        case = '-1'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError,
            'delay time must be greater than 0', ctp._cmd_delay, case)
        case = '65536'.split()
        self.assertRaisesRegex(ctp.CtpSyntaxError,
            'delay time must be less than {}'.format(2**16 - 1),
            ctp._cmd_delay, case)

class Test_parse_code(ut.TestCase):
    def setUp(self):
        self.res = [
            b'\x04\x80\x00',
            b'\x03\x00\x80',
            b'\x02\x03\x00',
            b'\x01\x04\x00'
        ]

    def test_valids(self):
        case = [
            'gnd 8\n',
            'vin 16\n',
            'set on 1 2\n',
            'check on 3 off rest\n'
        ]        
        # make sure the pin_state is reset
        for i in ctp._cmd_set.pin_state:
            ctp._cmd_set.pin_state[i] = False
        self.assertEqual(ctp.parse_code(case), self.res)

    def test_skips(self):
        # test for blank lines
        case = [
            'gnd 8\n',
            'vin 16\n',
            '\n',
            'set on 1 2\n',
            'check on 3 off rest\n'
        ]
        # make sure the pin_state is reset
        for i in ctp._cmd_set.pin_state:
            ctp._cmd_set.pin_state[i] = False
        self.assertEqual(ctp.parse_code(case), self.res)

        # test for whitespace lines
        case = [
            'gnd 8\n',
            'vin 16\n',
            '\t\n',
            'set on 1 2\n',
            'check on 3 off rest\n'
        ]
        # make sure the pin_state is reset
        for i in ctp._cmd_set.pin_state:
            ctp._cmd_set.pin_state[i] = False
        self.assertEqual(ctp.parse_code(case), self.res)
        case = [
            'gnd 8\n',
            'vin 16\n',
            '     \n',
            'set on 1 2\n',
            'check on 3 off rest\n'
        ]
        # make sure the pin_state is reset
        for i in ctp._cmd_set.pin_state:
            ctp._cmd_set.pin_state[i] = False
        self.assertEqual(ctp.parse_code(case), self.res)

        # test for comments
        case = [
            'gnd 8\n',
            'vin 16\n',
            '# comment\n',
            'set on 1 2\n',
            'check on 3 off rest\n'
        ]
        # make sure the pin_state is reset
        for i in ctp._cmd_set.pin_state:
            ctp._cmd_set.pin_state[i] = False
        self.assertEqual(ctp.parse_code(case), self.res)

    def test_extra_whitespace(self):
        case = [
            'gnd   8\n',
            'vin \t16\n',
            'set on 1 2\n',
            'check on 3 off rest\n'
        ]
        # make sure the pin_state is reset
        for i in ctp._cmd_set.pin_state:
            ctp._cmd_set.pin_state[i] = False
        self.assertEqual(ctp.parse_code(case), self.res)

def main():
    ut.main()

if __name__ == '__main__':
    main()