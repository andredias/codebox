error = 'error'                         # something doesn't run
warning = 'warning'                     # suspicious or could be optimized
coding_style = suggestion = info = 'info'     # coding style violation etc.

flake8 = {
    'E1': coding_style,  #  Indentation
    'E101': coding_style,  #  indentation contains mixed spaces and tabs
    'E111': coding_style,  #  indentation is not a multiple of four
    'E112': coding_style,  #  expected an indented block
    'E113': coding_style,  #  unexpected indentation
    'E114': coding_style,  #  indentation is not a multiple of four (comment)
    'E115': coding_style,  #  expected an indented block (comment)
    'E116': coding_style,  #  unexpected indentation (comment)
    'E121': coding_style,  #  continuation line under-indented for hanging indent
    'E122': coding_style,  #  continuation line missing indentation or outdented
    'E123': coding_style,  #  closing bracket does not match indentation of opening bracket’s line
    'E124': coding_style,  #  closing bracket does not match visual indentation
    'E125': coding_style,  #  continuation line with same indent as next logical line
    'E126': coding_style,  #  continuation line over-indented for hanging indent
    'E127': coding_style,  #  continuation line over-indented for visual indent
    'E128': coding_style,  #  continuation line under-indented for visual indent
    'E129': coding_style,  #  visually indented line with same indent as next logical line
    'E131': coding_style,  #  continuation line unaligned for hanging indent
    'E133': coding_style,  #  closing bracket is missing indentation
    'E2': coding_style,  #  Whitespace
    'E201': coding_style,  #  whitespace after ‘(‘
    'E202': coding_style,  #  whitespace before ‘)’
    'E203': coding_style,  #  whitespace before ‘:’
    'E211': coding_style,  #  whitespace before ‘(‘
    'E221': coding_style,  #  multiple spaces before operator
    'E222': coding_style,  #  multiple spaces after operator
    'E223': coding_style,  #  tab before operator
    'E224': coding_style,  #  tab after operator
    'E225': coding_style,  #  missing whitespace around operator
    'E226': coding_style,  #  missing whitespace around arithmetic operator
    'E227': coding_style,  #  missing whitespace around bitwise or shift operator
    'E228': coding_style,  #  missing whitespace around modulo operator
    'E231': coding_style,  #  missing whitespace after ‘,’
    'E241': coding_style,  #  multiple spaces after ‘,’
    'E242': coding_style,  #  tab after ‘,’
    'E251': coding_style,  #  unexpected spaces around keyword / parameter equals
    'E261': coding_style,  #  at least two spaces before inline comment
    'E262': coding_style,  #  inline comment should start with ‘# ‘
    'E265': coding_style,  #  block comment should start with ‘# ‘
    'E266': coding_style,  #  too many leading ‘#’ for block comment
    'E271': coding_style,  #  multiple spaces after keyword
    'E272': coding_style,  #  multiple spaces before keyword
    'E273': coding_style,  #  tab after keyword
    'E274': coding_style,  #  tab before keyword
    'E3': coding_style,  #  Blank line
    'E301': coding_style,  #  expected 1 blank line, found 0
    'E302': coding_style,  #  expected 2 blank lines, found 0
    'E303': coding_style,  #  too many blank lines (3)
    'E304': coding_style,  #  blank lines found after function decorator
    'E4': coding_style,  #  Import
    'E401': coding_style,  #  multiple imports on one line
    'E5': coding_style,  #  Line length
    'E501': coding_style,  #  line too long (82 > 79 characters)
    'E502': coding_style,  #  the backslash is redundant between brackets
    'E7': coding_style,  #  Statement
    'E701': coding_style,  #  multiple statements on one line (colon)
    'E702': coding_style,  #  multiple statements on one line (semicolon)
    'E703': coding_style,  #  statement ends with a semicolon
    'E704': coding_style,  #  multiple statements on one line (def)
    'E711': coding_style,  #  comparison to None should be ‘if cond is None:’
    'E712': coding_style,  #  comparison to True should be ‘if cond is True:’ or ‘if cond:’
    'E713': coding_style,  #  test for membership should be ‘not in’
    'E714': coding_style,  #  test for object identity should be ‘is not’
    'E721': coding_style,  #  do not compare types, use ‘isinstance()’
    'E731': coding_style,  #  do not assign a lambda expression, use a def
    'E9': error,  #  Runtime
    'E901': error,  #  SyntaxError or IndentationError
    'E902': error,  #  IOError
    'W1': warning,  #  Indentation warning
    'W191': warning,  #  indentation contains tabs
    'W2': coding_style,  #  Whitespace warning
    'W291': coding_style,  #  trailing whitespace
    'W292': coding_style,  #  no newline at end of file
    'W293': coding_style,  #  blank line contains whitespace
    'W3': coding_style,  #  Blank line warning
    'W391': coding_style,  #  blank line at end of file
    'W6': warning,  #  Deprecation warning
    'W601': warning,  #  has_key() is deprecated, use ‘in’
    'W602': warning,  #  deprecated form of raising exception
    'W603': warning,  #  ‘<>’ is deprecated, use ‘!=’
    'W604': warning,  #  backticks are deprecated, use ‘repr()’
}


pylint = {
    'C0102': coding_style,  # Black listed name "%s"
    'C0103': coding_style,  # Invalid %s name "%s"
    'C0111': info,  # Missing %s docstring
    'C0112': info,  # Empty %s docstring
    'C0121': coding_style,  # Missing required attribute "%s"
    'C0202': warning,  # Class method %s should have cls as first argument
    'C0203': coding_style,  # Metaclass method %s should have mcs as first argument
    'C0204': coding_style,  # Metaclass class method %s should have %s as first argument
    'C0301': coding_style,  # Line too long (%s/%s)
    'C0302': suggestion,  # Too many lines in module (%s)
    'C0303': coding_style,  # Trailing whitespace
    'C0304': coding_style,  # Final newline missing
    'C0321': coding_style,  # More than one statement on a single line
    'C0322': coding_style,  # Old: Operator not preceded by a space
    'C0323': coding_style,  # Old: Operator not followed by a space
    'C0324': coding_style,  # Old: Comma not followed by a space
    'C0325': suggestion,  # Unnecessary parens after %r keyword
    'C0326': coding_style,  # %s space %s %s %s\n%s
    'C1001': warning,  # Old-style class defined.
    'E0001': error,  # (syntax error raised for a module; message varies)
    'E0011': error,  # Unrecognized file option %r
    'E0012': error,  # Bad option value %r
    'E0100': error,  # __init__ method is a generator
    'E0101': error,  # Explicit return in __init__
    'E0102': error,  # %s already defined line %s
    'E0103': error,  # %r not properly in loop
    'E0104': error,  # Return outside function
    'E0105': error,  # Yield outside function
    'E0106': error,  # Return with argument inside generator
    'E0107': error,  # Use of the non-existent %s operator
    'E0108': error,  # Duplicate argument name %s in function definition
    'E0202': error,  # An attribute affected in %s line %s hide this method
    'E0203': error,  # Access to member %r before its definition line %s
    'E0211': error,  # Method has no argument
    'E0213': error,  # Method should have "self" as first argument
    'E0221': error,  # Interface resolved to %s is not a class
    'E0222': error,  # Missing method %r from %s interface
    'E0235': error,  # __exit__ must accept 3 arguments: type, value, traceback
    'E0501': error,  # Old: Non ascii characters found but no encoding specified (PEP 263)
    'E0502': error,  # Old: Wrong encoding specified (%s)
    'E0503': error,  # Old: Unknown encoding specified (%s)
    'E0601': error,  # Using variable %r before assignment
    'E0602': error,  # Undefined variable %r
    'E0603': error,  # Undefined variable name %r in __all__
    'E0604': error,  # Invalid object %r in __all__, must contain only strings
    'E0611': error,  # No name %r in module %r
    'E0701': error,  # Bad except clauses order (%s)
    'E0702': error,  # Raising %s while only classes, instances or string are allowed
    'E0710': error,  # Raising a new style class which doesn't inherit from BaseException
    'E0711': error,  # NotImplemented raised - should raise NotImplementedError
    'E0712': error,  # Catching an exception which doesn\'t inherit from BaseException: %s
    'E1001': error,  # Use of __slots__ on an old style class
    'E1002': error,  # Use of super on an old style class
    'E1003': error,  # Bad first argument %r given to super()
    'E1004': error,  # Missing argument to super()
    'E1101': error,  # %s %r has no %r member
    'E1102': error,  # %s is not callable
    'E1103': error,  # %s %r has no %r member (but some types could not be inferred)
    'E1111': error,  # Assigning to function call which doesn't return
    'E1120': error,  # No value passed for parameter %s in function call
    'E1121': error,  # Too many positional arguments for function call
    'E1122': error,  # Old: Duplicate keyword argument %r in function call
    'E1123': error,  # Passing unexpected keyword argument %r in function call
    'E1124': error,  # Parameter %r passed as both positional and keyword argument
    'E1125': error,  # Old: Missing mandatory keyword argument %r
    'E1200': error,  # Unsupported logging format character %r (%#02x) at index %d
    'E1201': error,  # Logging format string ends in middle of conversion specifier
    'E1205': error,  # Too many arguments for logging format string
    'E1206': error,  # Not enough arguments for logging format string
    'E1300': error,  # Unsupported format character %r (%#02x) at index %d
    'E1301': error,  # Format string ends in middle of conversion specifier
    'E1302': error,  # Mixing named and unnamed conversion specifiers in format string
    'E1303': error,  # Expected mapping for format string, not %s
    'E1304': error,  # Missing key %r in format string dictionary
    'E1305': error,  # Too many arguments for format string
    'E1306': error,  # Not enough arguments for format string
    'E1310': error,  # Suspicious argument in %s.%s call
    'F0001': error,  # (error prevented analysis; message varies)
    'F0002': error,  # %s: %s (message varies)
    'F0003': error,  # ignored builtin module %s
    'F0004': error,  # unexpected inferred value %s
    'F0010': error,  # error while code parsing: %s
    'F0202': error,  # Unable to check methods signature (%s / %s)
    'F0220': error,  # failed to resolve interfaces implemented by %s (%s)
    'F0321': error,  # Old: Format detection error in %r
    'F0401': error,  # Unable to import %s
    'I0001': warning,  # Unable to run raw checkers on built-in module %s
    'I0010': warning,  # Unable to consider inline option %r
    'I0011': warning,  # Locally disabling %s
    'I0012': warning,  # Locally enabling %s
    'I0013': warning,  # Ignoring entire file
    'I0014': warning,  # Used deprecated directive "pylint:disable-all" or "pylint:disable=all"
    'I0020': warning,  # Suppressed %s (from line %d)
    'I0021': warning,  # Useless suppression of %s
    'I0022': warning,  # Deprecated pragma "pylint:disable-msg" or "pylint:enable-msg"
    'R0201': suggestion,  # Method could be a function
    'R0401': warning,  # Cyclic import (%s)
    'R0801': info,  # Similar lines in %s files
    'R0901': suggestion,  # Too many ancestors (%s/%s)
    'R0902': suggestion,  # Too many instance attributes (%s/%s)
    'R0903': suggestion,  # Too few public methods (%s/%s)
    'R0904': suggestion,  # Too many public methods (%s/%s)
    'R0911': suggestion,  # Too many return statements (%s/%s)
    'R0912': suggestion,  # Too many branches (%s/%s)
    'R0913': suggestion,  # Too many arguments (%s/%s)
    'R0914': suggestion,  # Too many local variables (%s/%s)
    'R0915': suggestion,  # Too many statements (%s/%s)
    'R0921': warning,  # Abstract class not referenced
    'R0922': info,  # Abstract class is only referenced %s times
    'R0923': warning,  # Interface not implemented
    'RP0001': info,  #  Messages by category
    'RP0002': info,  #  % errors / warnings by module
    'RP0003': info,  #  Messages
    'RP0004': info,  #  Global evaluation
    'RP0101': info,  #  Statistics by type
    'RP0401': info,  #  External dependencies
    'RP0402': info,  #  Modules dependencies graph
    'RP0701': info,  #  Raw metrics
    'RP0801': info,  #  Duplication
    'W0101': warning,  # Unreachable code
    'W0102': warning,  # Dangerous default value %s as argument
    'W0104': warning,  # Statement seems to have no effect
    'W0105': warning,  # String statement has no effect
    'W0106': warning,  # Expression "%s" is assigned to nothing
    'W0107': warning,  # Unnecessary pass statement
    'W0108': warning,  # Lambda may not be necessary
    'W0109': warning,  # Duplicate key %r in dictionary
    'W0110': warning,  # map/filter on lambda could be replaced by comprehension
    'W0120': warning,  # Else clause on loop without a break statement
    'W0121': warning,  # Use raise ErrorClass(args) instead of raise ErrorClass, args.
    'W0122': warning,  # Use of exec
    'W0141': warning,  # Used builtin function %r
    'W0142': warning,  # Used * or ** magic
    'W0150': warning,  # %s statement in finally block may swallow exception
    'W0199': warning,  # Assert called on a 2-uple. Did you mean \'assert x,y\'?
    'W0201': warning,  # Attribute %r defined outside __init__
    'W0211': warning,  # Static method with %r as first argument
    'W0212': warning,  # Access to a protected member %s of a client class
    'W0221': warning,  # Arguments number differs from %s method
    'W0222': warning,  # Signature differs from %s method
    'W0223': warning,  # Method %r is abstract in class %r but is not overridden
    'W0231': warning,  # __init__ method from base class %r is not called
    'W0232': warning,  # Class has no __init__ method
    'W0233': warning,  # __init__ method from a non direct base class %r is called
    'W0234': warning,  # iter returns non-iterator
    'W0301': warning,  # Unnecessary semicolon
    'W0311': warning,  # Bad indentation. Found %s %s, expected %s
    'W0312': warning,  # Found indentation with %ss instead of %ss
    'W0331': warning,  # Use of the <> operator
    'W0332': warning,  # Use of "l" as long integer identifier
    'W0333': warning,  # Use of the `` operator
    'W0401': warning,  # Wildcard import %s
    'W0402': warning,  # Uses of a deprecated module %r
    'W0403': warning,  # Relative import %r, should be %r
    'W0404': warning,  # Reimport %r (imported line %s)
    'W0406': warning,  # Module import itself
    'W0410': warning,  # __future__ import is not the first non docstring statement
    'W0511': warning,  # (warning notes in code comments; message varies)
    'W0512': warning,  # Cannot decode using encoding "%s", unexpected byte at position %d
    'W0601': warning,  # Global variable %r undefined at the module level
    'W0602': warning,  # Using global for %r but no assigment is done
    'W0603': warning,  # Using the global statement
    'W0604': warning,  # Using the global statement at the module level
    'W0611': warning,  # Unused import %s
    'W0612': warning,  # Unused variable %r
    'W0613': warning,  # Unused argument %r
    'W0614': warning,  # Unused import %s from wildcard import
    'W0621': warning,  # Redefining name %r from outer scope (line %s)
    'W0622': warning,  # Redefining built-in %r
    'W0623': warning,  # Redefining name %r from %s in exception handler
    'W0631': warning,  # Using possibly undefined loop variable %r
    'W0632': warning,  # Possible unbalanced tuple unpacking with sequence%s: …
    'W0633': warning,  # Attempting to unpack a non-sequence%s
    'W0701': warning,  # Raising a string exception
    'W0702': warning,  # No exception type(s) specified
    'W0703': warning,  # Catching too general exception %s
    'W0704': warning,  # Except doesn't do anything
    'W0710': warning,  # Exception doesn't inherit from standard "Exception" class
    'W0711': warning,  # Exception to catch is the result of a binary "%s" operation
    'W0712': warning,  # Implicit unpacking of exceptions is not supported in Python 3
    'W1001': warning,  # Use of "property" on an old style class
    'W1111': warning,  # Assigning to function call which only returns None
    'W1201': warning,  # Specify string format arguments as logging function parameters
    'W1300': warning,  # Format string dictionary key should be a string, not %s
    'W1301': warning,  # Unused key %r in format string dictionary
    'W1401': warning,  # Anomalous backslash in string: \'%s\'. String constant might be missing an r prefix.
    'W1402': warning,  # Anomalous Unicode escape in byte string: \'%s\'. String constant might be missing an r or u prefix.
    'W1501': warning,  # "%s" is not a valid mode for open.
}

cpplint = {
    'build/class': warning,
    'build/c++11': warning,
    'build/deprecated': warning,
    'build/endif_comment': warning,
    'build/explicit_make_pair': warning,
    'build/forward_decl': warning,
    'build/header_guard': warning,
    'build/include': warning,
    'build/include_alpha': warning,
    'build/include_order': warning,
    'build/include_what_you_use': warning,
    'build/namespaces': warning,
    'build/printf_format': warning,
    'build/storage_class': warning,
    'legal/copyright': info,
    'readability/alt_tokens': coding_style,
    'readability/braces': coding_style,
    'readability/casting': coding_style,
    'readability/check': coding_style,
    'readability/constructors': coding_style,
    'readability/fn_size': coding_style,
    'readability/function': coding_style,
    'readability/inheritance': coding_style,
    'readability/multiline_comment': coding_style,
    'readability/multiline_string': coding_style,
    'readability/namespace': coding_style,
    'readability/nolint': coding_style,
    'readability/nul': coding_style,
    'readability/strings': coding_style,
    'readability/todo': coding_style,
    'readability/utf8': coding_style,
    'runtime/arrays': error,
    'runtime/casting': error,
    'runtime/explicit': error,
    'runtime/int': error,
    'runtime/init': error,
    'runtime/invalid_increment': error,
    'runtime/member_string_references': error,
    'runtime/memset': error,
    'runtime/indentation_namespace': error,
    'runtime/operator': error,
    'runtime/printf': error,
    'runtime/printf_format': error,
    'runtime/references': error,
    'runtime/string': error,
    'runtime/threadsafe_fn': error,
    'runtime/vlog': error,
    'whitespace/blank_line': coding_style,
    'whitespace/braces': coding_style,
    'whitespace/comma': coding_style,
    'whitespace/comments': coding_style,
    'whitespace/empty_conditional_body': coding_style,
    'whitespace/empty_loop_body': coding_style,
    'whitespace/end_of_line': coding_style,
    'whitespace/ending_newline': coding_style,
    'whitespace/forcolon': coding_style,
    'whitespace/indent': coding_style,
    'whitespace/line_length': coding_style,
    'whitespace/newline': coding_style,
    'whitespace/operators': coding_style,
    'whitespace/parens': coding_style,
    'whitespace/semicolon': coding_style,
    'whitespace/tab': coding_style,
    'whitespace/todo': coding_style,
}

rubocop = {
    'R': warning,  # Refactor
    'C': coding_style,  # Convention
    'E': error,  # Error
    'F': error,  # Fatal
    'W': warning,  # Warning
}
