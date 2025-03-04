import textwrap

from parameterized import parameterized

import hedy
from hedy import Command
from tests.Tester import HedyTester


class TestsLevel4(HedyTester):
    level = 4
    '''
    Tests should be ordered as follows:
     * commands in the order of hedy.py e.g. for level 1: ['print', 'ask', 'echo', 'turn', 'forward']
     * combined tests
     * markup tests
     * negative tests

    Naming conventions are like this:
     * single keyword positive tests are just keyword or keyword_special_case
     * multi keyword positive tests are keyword1_keywords_2
     * negative tests should be situation_gives_exception
    '''

    #
    # print tests
    #
    def test_print_single_quoted_text(self):
        code = "print 'hallo wereld!'"
        expected = "print(f'hallo wereld!')"

        self.multi_level_tester(
            code=code,
            max_level=11,
            expected=expected)

    def test_print_double_quoted_text(self):
        code = 'print "hallo wereld!"'
        expected = "print(f'hallo wereld!')"

        self.multi_level_tester(
            code=code,
            max_level=11,
            expected=expected)

    def test_print_line_with_spaces_works(self):
        code = "print 'hallo'\n      \nprint 'hallo'"
        expected = "print(f'hallo')\n\nprint(f'hallo')"
        expected_commands = [Command.print, Command.print]

        self.multi_level_tester(
            code=code,
            expected=expected,
            expected_commands=expected_commands,
            max_level=7)

    def test_print_single_quoted_text_with_inner_double_quote(self):
        code = """print 'quote is "'"""
        expected = """print(f'quote is "')"""

        self.multi_level_tester(
            code=code,
            max_level=11,
            expected=expected)

    def test_print_double_quoted_text_with_inner_single_quote(self):
        code = '''print "It's me"'''
        expected = """print(f'It\\'s me')"""

        self.multi_level_tester(
            code=code,
            max_level=11,
            expected=expected)

    def test_print_with_space_gives_invalid(self):
        code = " print 'Hallo welkom bij Hedy!'"

        self.multi_level_tester(
            code=code,
            exception=hedy.exceptions.InvalidSpaceException,
            max_level=7)

    def test_print_no_space(self):
        code = "print'hallo wereld!'"
        expected = "print(f'hallo wereld!')"

        self.multi_level_tester(
            code=code,
            max_level=11,
            expected=expected)

    def test_print_comma(self):
        code = "print 'Hi, I am Hedy'"
        expected = "print(f'Hi, I am Hedy')"
        self.multi_level_tester(
            code=code,
            max_level=11,
            expected=expected
        )

    def test_print_slash(self):
        code = "print 'Yes/No'"
        expected = "print(f'Yes/No')"

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_print_backslash(self):
        code = "print 'Yes\\No'"
        expected = "print(f'Yes\\\\No')"
        output = "Yes\\No"

        self.multi_level_tester(
            code=code,
            expected=expected,
            output=output,
            max_level=11,
            translate=True
        )

    def test_print_with_backslash_at_end(self):
        code = "print 'Welcome to \\'"
        expected = "print(f'Welcome to \\\\')"
        self.multi_level_tester(
            code=code,
            max_level=11,
            expected=expected,
            translate=True
        )

    def test_print_with_spaces(self):
        code = "print        'hallo!'"
        expected = "print(f'hallo!')"

        self.multi_level_tester(
            code=code,
            max_level=11,
            expected=expected
        )

    def test_print_asterisk(self):
        code = "print '*Jouw* favoriet is dus kleur'"
        expected = "print(f'*Jouw* favoriet is dus kleur')"

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_print_without_quotes_gives_error_from_grammar(self):
        # in some cases, there is no variable confusion since 'hedy 123' can't be a variable
        # then we can immediately raise the no quoted exception

        code = "print hedy 123"

        self.multi_level_tester(
            code=code,
            max_level=5,
            exception=hedy.exceptions.UnquotedTextException,
            extra_check_function=lambda c: c.exception.arguments['line_number'] == 1
        )

    def test_print_without_quotes_gives_error_from_transpiler(self):
        # in other cases, there might be two different problems
        # is this unquoted? or did we forget an initialization of a variable?

        # a quick analysis of the logs shows that in most cases quotes are forgotten
        # so we will only raise var if there is a variable that is a bit similar (see next test)

        code = "print hallo wereld"

        self.multi_level_tester(
            code=code,
            max_level=17,
            exception=hedy.exceptions.UnquotedTextException,
        )

    def test_ask_without_quotes_gives_error_from_grammar(self):
        # same as print for level 4
        code = "pietje is ask hedy 123"

        self.multi_level_tester(
            code=code,
            max_level=4,
            exception=hedy.exceptions.UnquotedTextException
        )

    def test_place_holder_no_space(self):
        # same as print for level 4
        code = "print _Escape from the haunted house!_"

        self.multi_level_tester(
            code=code,
            max_level=11,
            exception=hedy.exceptions.CodePlaceholdersPresentException
        )

    def test_ask_without_quotes_gives_error_from_transpiler(self):
        # same as print
        code = "antwoord is ask hallo wereld"

        self.multi_level_tester(
            code=code,
            max_level=17,
            exception=hedy.exceptions.UnquotedTextException,
        )

    def test_print_similar_var_gives_error(self):
        # continuing: is this unquoted? or did we forget an initialization of a variable?

        # a quick analysis of the logs shows that in most cases quotes are forgotten
        # so we will only raise var if there is a variable that is a bit similar (see next test)

        code = textwrap.dedent("""\
            werld is ask 'tegen wie zeggen we hallo?'
            print hallo wereld""")

        self.multi_level_tester(
            code=code,
            max_level=17,
            exception=hedy.exceptions.UndefinedVarException,
            extra_check_function=lambda c: c.exception.arguments['line_number'] == 2
        )

    @parameterized.expand(HedyTester.quotes)
    def test_print_without_opening_quote_gives_error(self, q):
        code = f"print hedy 123{q}"
        self.multi_level_tester(
            code,
            max_level=6,
            exception=hedy.exceptions.UnquotedTextException
        )

    @parameterized.expand(HedyTester.quotes)
    def test_print_without_closing_quote_gives_error(self, q):
        code = f"print {q}hedy 123"
        self.multi_level_tester(
            code,
            max_level=6,
            exception=hedy.exceptions.UnquotedTextException
        )

    def test_print_single_quoted_text_var(self):
        code = textwrap.dedent("""\
        naam is 'Hedy'
        print 'ik heet ' naam""")

        expected = textwrap.dedent("""\
        naam = '\\'Hedy\\''
        print(f'ik heet {naam}')""")

        self.multi_level_tester(
            max_level=11,
            code=code,
            expected=expected
        )

    def test_print_double_quoted_text_var(self):
        code = textwrap.dedent("""\
        naam is "Hedy"
        print 'ik heet ' naam""")

        expected = textwrap.dedent("""\
        naam = '"Hedy"'
        print(f'ik heet {naam}')""")

        self.multi_level_tester(
            max_level=11,
            code=code,
            expected=expected
        )

    # issue 1795
    def test_print_quoted_var_reference(self):
        code = textwrap.dedent("""\
        naam is 'Daan'
        woord1 is zomerkamp
        print 'naam' ' is naar het' 'woord1'""")

        expected = textwrap.dedent("""\
        naam = '\\'Daan\\''
        woord1 = 'zomerkamp'
        print(f'naam is naar hetwoord1')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    #
    # Test comment
    #
    def test_print_comment(self):
        code = "print 'Hallo welkom bij Hedy!' # This is a comment"
        expected = "print(f'Hallo welkom bij Hedy!')"
        output = 'Hallo welkom bij Hedy!'

        self.multi_level_tester(
            max_level=11,
            code=code,
            expected=expected,
            output=output
        )

    def test_assign_comment(self):
        code = 'test is "Welkom bij Hedy" # This is a comment'
        expected = 'test = \'"Welkom bij Hedy" \''
        self.multi_level_tester(
            max_level=11,
            code=code,
            expected=expected
        )

    #
    # ask tests
    #
    def test_ask_single_quoted_text(self):
        code = "details is ask 'tell me more'"
        expected = "details = input(f'tell me more')"

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_ask_double_quoted_text(self):
        code = 'details is ask "tell me more"'
        expected = "details = input(f'tell me more')"

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_ask_single_quoted_text_with_inner_double_quote(self):
        code = """details is ask 'say "no"'"""
        expected = """details = input(f'say "no"')"""

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_ask_double_quoted_text_with_inner_single_quote(self):
        code = f'''details is ask "say 'no'"'''
        expected = '''details = input(f'say \\'no\\'')'''

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_ask_without_quotes_gives_error(self):
        code = "kleur is ask Hedy 123"
        self.single_level_tester(code, exception=hedy.exceptions.HedyException)

    def test_ask_text_without_quotes_gives_error(self):
        code = "var is ask hallo wereld"

        self.multi_level_tester(
            code=code,
            max_level=17,
            exception=hedy.exceptions.UndefinedVarException,
        )

    @parameterized.expand(HedyTester.quotes)
    def test_ask_without_opening_quote_gives_error(self, q):
        code = f"kleur is ask Hedy 123{q}"
        self.single_level_tester(code, exception=hedy.exceptions.UnquotedTextException)

    @parameterized.expand(HedyTester.quotes)
    def test_ask_without_closing_quote_gives_error(self, q):
        code = f"kleur is ask {q}Hedy 123"
        self.single_level_tester(code, exception=hedy.exceptions.UnquotedTextException)

    def test_ask_with_comma(self):
        code = textwrap.dedent("""\
        dieren is ask 'hond, kat, kangoeroe'
        print dieren""")

        expected = textwrap.dedent("""\
        dieren = input(f'hond, kat, kangoeroe')
        print(f'{dieren}')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    @parameterized.expand(HedyTester.quotes)
    def test_ask_es(self, q):
        code = f"""color is ask {q}Cuál es tu color favorito?{q}"""
        expected = f"""color = input(f'Cuál es tu color favorito?')"""

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    @parameterized.expand(HedyTester.quotes)
    def test_ask_bengali_var(self, q):
        code = textwrap.dedent(f"""\
        রং is ask {q}আপনার প্রিয় রং কি?{q}
        print রং {q} is আপনার প্রিয{q}""")

        expected = textwrap.dedent("""\
        রং = input(f'আপনার প্রিয় রং কি?')
        print(f'{রং} is আপনার প্রিয')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_ask_list_random(self):
        code = textwrap.dedent("""\
        colors is orange, blue, green
        favorite is ask 'Is your fav color ' colors at random""")

        expected = textwrap.dedent("""\
        colors = ['orange', 'blue', 'green']
        favorite = input(f'Is your fav color {random.choice(colors)}')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_ask_list_access_index(self):
        code = textwrap.dedent("""\
        colors is orange, blue, green
        favorite is ask 'Is your fav color ' colors at 1""")

        expected = textwrap.dedent("""\
        colors = ['orange', 'blue', 'green']
        favorite = input(f'Is your fav color {colors[1-1]}')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_ask_string_var(self):
        code = textwrap.dedent("""\
        color is orange
        favorite is ask 'Is your fav color ' color""")

        expected = textwrap.dedent("""\
        color = 'orange'
        favorite = input(f'Is your fav color {color}')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_ask_integer_var(self):
        code = textwrap.dedent("""\
        number is 10
        favorite is ask 'Is your fav number' number""")

        expected = textwrap.dedent("""\
        number = '10'
        favorite = input(f'Is your fav number{number}')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    #
    # sleep tests
    #
    def test_sleep_with_input_variable(self):
        code = textwrap.dedent("""\
            n is ask "how long"
            sleep n""")
        expected = HedyTester.dedent(
            "n = input(f'how long')",
            HedyTester.sleep_command_transpiled("n"))

        self.multi_level_tester(max_level=11, code=code, expected=expected)

    #
    # assign tests
    #
    def test_assign_print(self):
        code = textwrap.dedent("""\
        naam is Hedy
        print 'ik heet' naam""")

        expected = textwrap.dedent("""\
        naam = 'Hedy'
        print(f'ik heet{naam}')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_assign_underscore(self):
        code = textwrap.dedent("""\
        voor_naam is Hedy
        print 'ik heet ' voor_naam""")

        expected = textwrap.dedent("""\
        voor_naam = 'Hedy'
        print(f'ik heet {voor_naam}')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_assign_period(self):
        code = "period is ."
        expected = "period = '.'"

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_assign_list_values_with_inner_single_quotes(self):
        code = textwrap.dedent(f"""\
          taart is 'appeltaart, choladetaart, kwarktaart'
          print 'we bakken een ' taart at random""")

        expected = HedyTester.dedent("taart = ['\\'appeltaart', 'choladetaart', 'kwarktaart\\'']",
                                     HedyTester.list_access_transpiled('random.choice(taart)'),
                                     "print(f'we bakken een {random.choice(taart)}')")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_assign_list_values_with_inner_double_quotes(self):
        code = textwrap.dedent(f"""\
          taart is "appeltaart, choladetaart, kwarktaart"
          print 'we bakken een ' taart at random""")

        expected = HedyTester.dedent("taart = ['\"appeltaart', 'choladetaart', 'kwarktaart\"']",
                                     HedyTester.list_access_transpiled('random.choice(taart)'),
                                     "print(f'we bakken een {random.choice(taart)}')")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_assign_list_with_single_quoted_values(self):
        code = textwrap.dedent(f"""\
        taart is 'appeltaart', 'choladetaart', 'kwarktaart'
        print 'we bakken een' taart at random""")

        expected = HedyTester.dedent("taart = ['\\'appeltaart\\'', '\\'choladetaart\\'', '\\'kwarktaart\\'']",
                                     HedyTester.list_access_transpiled('random.choice(taart)'),
                                     "print(f'we bakken een{random.choice(taart)}')")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_assign_list_with_double_quoted_values(self):
        code = textwrap.dedent(f"""\
        taart is "appeltaart, choladetaart, kwarktaart"
        print 'we bakken een' taart at random""")

        expected = HedyTester.dedent("taart = ['\"appeltaart', 'choladetaart', 'kwarktaart\"']",
                                     HedyTester.list_access_transpiled('random.choice(taart)'),
                                     "print(f'we bakken een{random.choice(taart)}')")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_assign_single_quoted_text(self):
        code = """message is 'Hello welcome to Hedy.'"""
        expected = """message = '\\'Hello welcome to Hedy.\\''"""
        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_assign_double_quoted_text(self):
        code = '''message is "Hello welcome to Hedy."'''
        expected = """message = '"Hello welcome to Hedy."'"""
        self.multi_level_tester(code=code, expected=expected, max_level=11)

    #
    # add/remove tests
    #
    def test_add_ask_to_list(self):
        code = textwrap.dedent("""\
        color is ask 'what is your favorite color?'
        colors is green, red, blue
        add color to colors
        print colors at random""")
        expected = HedyTester.dedent("color = input(f'what is your favorite color?')",
                                     "colors = ['green', 'red', 'blue']",
                                     "colors.append(color)",
                                     HedyTester.list_access_transpiled("random.choice(colors)"),
                                     "print(f'{random.choice(colors)}')")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_remove_ask_from_list(self):
        code = textwrap.dedent("""\
        colors is green, red, blue
        color is ask 'what color to remove?'
        remove color from colors
        print colors at random""")

        expected = HedyTester.dedent("colors = ['green', 'red', 'blue']",
                                     "color = input(f'what color to remove?')",
                                     HedyTester.remove_transpiled('colors', 'color'),
                                     HedyTester.list_access_transpiled('random.choice(colors)'),
                                     "print(f'{random.choice(colors)}')")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    #
    # combined tests
    #
    def test_assign_print_chinese(self):
        code = textwrap.dedent("""\
        你世界 is 你好世界
        print 你世界""")

        expected = textwrap.dedent("""\
        你世界 = '你好世界'
        print(f'{你世界}')""")

        self.multi_level_tester(code=code, expected=expected, max_level=11)

    def test_ask_forward(self):
        code = textwrap.dedent("""\
        afstand is ask 'hoe ver dan?'
        forward afstand""")

        expected = HedyTester.dedent(
            "afstand = input(f'hoe ver dan?')",
            HedyTester.forward_transpiled('afstand', self.level))

        self.multi_level_tester(
            max_level=11,
            code=code,
            expected=expected,
            extra_check_function=self.is_turtle()
        )

    #
    # negative tests
    #
    def test_var_undefined_error_message(self):
        code = textwrap.dedent("""\
        naam is Hedy
        print 'ik heet ' name""")

        self.multi_level_tester(
            code=code,
            max_level=11,
            exception=hedy.exceptions.UndefinedVarException
        )

    # issue 375
    def test_program_gives_hedy_parse_exception(self):
        code = textwrap.dedent("""\
        is Foobar
        print welcome""")

        self.multi_level_tester(
            code=code,
            max_level=11,
            exception=hedy.exceptions.ParseException,
            extra_check_function=lambda c: c.exception.error_location[0] == 1 and c.exception.error_location[1] == 1
        )

    def test_quoted_text_gives_error(self):
        code = 'competitie die gaan we winnen'

        self.multi_level_tester(code=code, exception=hedy.exceptions.MissingCommandException)

    def test_repair_incorrect_print_argument(self):
        code = "print ,'Hello'"

        self.multi_level_tester(
            code=code,
            exception=hedy.exceptions.ParseException,
            extra_check_function=lambda c: c.exception.fixed_code == "print 'Hello'"
        )

    def test_lonely_text(self):
        code = "'Hello'"
        self.multi_level_tester(
            code=code,
            exception=hedy.exceptions.LonelyTextException
        )

    def test_clear(self):
        code = "clear"
        expected = textwrap.dedent("""\
        extensions.clear()
        try:
            # If turtle is being used, reset canvas
            t.hideturtle()
            turtle.resetscreen()
            t.left(90)
            t.showturtle()
        except NameError:
            pass""")

        self.multi_level_tester(code=code, expected=expected)
