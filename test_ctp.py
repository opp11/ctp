import unittest as ut
import ctp

class TestCtp(ut.TestCase):
    def test_is_keyword(self):
        # test valid cases
        self.assertTrue(ctp._is_keyword('check'))
        self.assertTrue(ctp._is_keyword('set'))
        self.assertTrue(ctp._is_keyword('vin'))
        self.assertTrue(ctp._is_keyword('delay'))
        self.assertTrue(ctp._is_keyword('rest'))

        # test invalid cases
        self.assertFalse(ctp._is_keyword(10))
        self.assertFalse(ctp._is_keyword(10.2))
        self.assertFalse(ctp._is_keyword('habla'))
        self.assertFalse(ctp._is_keyword(['vin', 'check']))
        self.assertFalse(ctp._is_keyword(['check', 'vin']))
        self.assertFalse(ctp._is_keyword(['check', 'set']))

    def test_is_pin(self):
        # test valid cases
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

        # test invalid cases
        self.assertFalse(ctp._is_pin('0'))
        self.assertFalse(ctp._is_pin('17'))
        self.assertFalse(ctp._is_pin('-1'))     
        self.assertFalse(ctp._is_pin('habla'))

    def test_pins_to_arg(self):
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

        case = [ True, True, True, True, False ]
        with self.assertRaises(TypeError):
            ctp._pins_to_arg(case)

    def test_get_pin_vals(self):
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

        case = 'habla 1'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)
        case = 'set habla'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)
        case = 'set on habla'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)
        case = 'set on 1, 2'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)

        case = '1'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)
        case = 'rest'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)
        case = 'on rest 2'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)
        case = 'on rest off 1'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)
        case = 'on 1 1'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)
        case = 'on 1 off 1'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._get_pin_vals, case)

    def test_cmd_check(self):
        case = 'on 1 2 off rest'.split()
        self.assertEqual(ctp._cmd_check(case), b'\x01\x03\x00')
        case = 'on rest'.split()
        self.assertEqual(ctp._cmd_check(case), b'\x01\xff\xff')
        case = 'on 1 2'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_check, case)

    def test_cmd_set(self):
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

    def test_cmd_vin(self):
        case = '5 14 15 16'.split()
        self.assertEqual(ctp._cmd_vin(case), b'\x03\x10\xe0')
        case = '16'.split()
        self.assertEqual(ctp._cmd_vin(case), b'\x03\x00\x80')

        case = '1 2'
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_vin, case)
        case = '17'
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_vin, case)
        case = 'habla'
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_vin, case)

    def test_cmd_gnd(self):
        case = '8 12'.split()
        self.assertEqual(ctp._cmd_gnd(case), b'\x04\x80\x08')
        case = '12'.split()
        self.assertEqual(ctp._cmd_gnd(case), b'\x04\x00\x08')

        case = '1 2'
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_gnd, case)
        case = '17'
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_gnd, case)
        case = 'habla'
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_gnd, case)

    def test_cmd_delay(self):
        case = '100'.split()
        self.assertEqual(ctp._cmd_delay(case), b'\x05\x64\x00')
        case = '0'.split()
        self.assertEqual(ctp._cmd_delay(case), b'\x05\x00\x00')
        case = '65535'.split()
        self.assertEqual(ctp._cmd_delay(case), b'\x05\xff\xff')

        case = 'habla'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_delay, case)
        case = '100 100'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_delay, case)
        case = '-1'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_delay, case)
        case = '65536'.split()
        self.assertRaises(ctp.CtpSyntaxError, ctp._cmd_delay, case)

def main():
    ut.main()

if __name__ == '__main__':
    main()