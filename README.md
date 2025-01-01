# argparse2
Enhanced argparse (argument parsing for Python).

This is a modified argparse from [CPython](https://github.com/python/cpython "CPython") (2025.01.01) with added features.

Most features are opt-in, so this is close to the official version by default.
Thus, if you're not interested in any of these features, you're better off using the official argparse !

On to the good stuff :

* [Clearer error message formatting](#clearer-error-message-formatting)
* [Options used more than once](#options-used-more-than-once)
* [Help formatting customization](#help-formatting-customization)
  + [Smarter `ArgumentDefaultsHelpFormatter`](#smarter--argumentdefaultshelpformatter-)
  + [A new `ArgumentQualifHelpFormatter`](#a-new--argumentqualifhelpformatter-)
  + [`RawDescriptionHelpFormatter` replaced with `raw_description=True`](#-rawdescriptionhelpformatter--replaced-with--raw-description-true-)
  + [Forced line breaks](#forced-line-breaks)
* [Short help](#short-help)
  + [New action `short_help` :](#new-action--short-help---)
  + [Example use](#example-use)


## Clearer error message formatting
This is the most visible of the *forced* new features :

    $ python prog.py -b b1 --bucket b2
    
      Usage: prog.py -b <Bucket> -r <root_folder> -i <input_file> [<input_file> ...] [-s <char>] [-w] [-k <max_seconds>]
                     [-o <output_file>] [-h] [--help] [-v]
    
    !! Error: argument -b/--bucket used more than once :
    
         -b b1
         --bucket b2
    
      Please provide one single S3 bucket !

As you can see, this makes it plenty clear why the parsing failed and tries to give the most precise error message possible.

Here you already see a few new features :

- You can define an option as being single-use (can not repeat on the command line)
- If you hate the "!! Error:" prefix, you can customize it : `argparse.ArgumentParser(.. , error_tag='>>> Error', .. )` (default is "Error")
- And you can add a custom error message (last line) to explain why the argument shouldn't be provided more than once.

Keep reading !

## Options used more than once
If it makes sense, any option can be limited from appearing multiple times on the command line now via the new argument `max_use_count` :
```python
parser.add_argument('-b', '--bucket', .. , max_use_count=1, max_use_err='\n  Please provide one single S3 bucket !\n' )
```
Default is 0 (disabled). Only positive integers allowed.

You can additionnaly provide a `max_use_err` string to lecture the user about all the evils of his redundant behaviour.

## Help formatting customization
### Smarter `ArgumentDefaultsHelpFormatter`
If the help string you provide already talks about defaults (containes "default " or `%(default)s`), no default indication is appended.
```python
import argparse2 as argparse
MAX_AGE = 40 # seconds
...
parser = argparse.ArgumentParser(.., formatter_class=argparse.ArgumentQualifHelpFormatter, ..) # or ArgumentDefaultsHelpFormatter
parser.add_argument('-k', '--skip-recent', nargs=1, metavar="<max_seconds>", action='extend', type=int,
default=[MAX_AGE], help='Default is to .. %ds ago.' %MAX_AGE)
```
Formatted help : because default is described in the help string, no '(default : 40)' is appended.   

    $ prog --help
     ...
    -k, --skip-recent <max_seconds>
                            Recommended. Default is to skip files modified less than 40s ago.
Also : if default of is of type file, for stdin/out/err (at least !), you don't end up with a thorny `(default : class '_io.TextIOWrapper' ..)` but with a clear and concise `(default : stdout)`.

The "Recommended" indication was added automatically because this formatter was enhanced into a new one :

### A new `ArgumentQualifHelpFormatter`
```python
parser = argparse.ArgumentParser(.. , formatter_class=argparse.ArgumentQualifHelpFormatter, .. )
parser.add_argument('-b', .. , required=True, .. )
parser.add_argument('-k', .. , recommend=True, .. )

```
    $ python prog.py  --help
    ...
    -b, --bucket <Bucket>   Required. Set S3 bucket.
    -k, --skip-recent <max_seconds>
                            Recommended. Default is to skip files modified less than 40s ago.
This new `formatter_class` supports the `recommend` argument with the existing `required` one, and help strings are qualified accordingly.

Now, how can you enjoy these stellar enhancements if you want a raw description (provided by `RawDescriptionHelpFormatter`) at the same time ?

### `RawDescriptionHelpFormatter` replaced with `raw_description=True`
If you want raw description in argparse, you loose the ability to enjoy features from other `formatter_class`es.
This has been isolated into a new `raw_description` argument :

    parser = argparse.ArgumentParser(.. , formatter_class=argparse.ArgumentQualifHelpFormatter, raw_description=True, .. )
This separates how description & help strings are formatted.

### Forced line breaks
Even with `RawTextHelpFormatter`, your help string with line breaks :
```python
parser.add_argument('-k', .. , help='Default is to skip files modified less than %ds ago.\
If set : skip files not older than <max_seconds> seconds. Adjust to your specific situation.\
Set to 0 to disable (at your own risks !). Note that even in this case if ETag changes\
during the copy operation, the file will still be skipped (it is being actively modified !).' %MAX_AGE )
```
is compacted to :

    -k, --skip-recent <max_seconds>
                      Recommended. Default is to skip files modified less than 40s ago. If set : skip files not older than
                      <max_seconds> seconds. Adjust to your specific situation. Set to 0 to disable (at your own risks !). Note that
                      even in this case if ETag changes during the copy operation, the file will still be skipped (it is being
                      actively modified !).
Maybe you wanted an easier to read :

    -k, --skip-recent <max_seconds>
                      Recommended. Default is to skip files modified less than 40s ago.
                      If set : skip files not older than <max_seconds> seconds. Adjust to your specific situation.
                      Set to 0 to disable (at your own risks !). Note that even in this case if ETag changes during the copy operation,
                      the file will still be skipped (it is being actively modified !).
Now you can force line breaks in help strings by inserting `@NL@` tags where needed :
```python
parser.add_argument('-k', .. , help='Default is to skip files modified less than %ds ago.@NL@\
If set : skip files not older than <max_seconds> seconds. Adjust to your specific situation.@NL@\
Set to 0 to disable (at your own risks !). Note that even in this case if ETag changes\
during the copy operation, the file will still be skipped (it is being actively modified !).' %MAX_AGE )
```
You can customize the special tag `@NL@` via a new argument to `argparse.ArgumentParser(.. , NL='<br>', ..)`

## Short help
An old user of your program will be annoyed more than anything else by a long help message (not under your control : if your program has many awsome features that you worked hard to implement, there has to be corresponding help strings !).

Yes, but this is an advanced user of your craft, and, especially if you have many options, he doesn't need the full help details, but a quick description of the options, with maybe a concise expressive example (thank you), right ? (so he can be reassured rarely used option '-b' really exists, and does what he thinks !)

He wants the 
### New action `short_help` :
```python
add_argument('-h', action='short_help', .. )
```
This new action consumes a new argument called `desc` :
```python
# Provide 'desc' strings (these can be %(help)s if help string is short enough) :
add_argument('-b', '--bucket', required=True, nargs=1, action='extend', help='Set S3 bucket.', desc='%(help)s', .. )
add_argument('-r', '--root', required=True, nargs=1, action='store', help='Set root folder on S3.', desc='%(help)s', .. )
...
add_argument('--help', '--full-help', action='help', help='Show this help message and exit.', desc='show full help')
add_argument('-h', action='short_help', .. )   # <<<<<<<<<<<< short_help
add_argument('-v', '--version', action='version', desc="show program's version", help='.. )
```
Short help :

    $ python prog.py  -h
    
      Usage : prog.py -b <Bucket> -r <root_folder> -i <input_file> [<input_file> ...] [-s <char>] [-w] [-k <max_seconds>]
                         [-o <output_file>] [-h] [--help] [-v]

        -b <Bucket>        : set S3 bucket.
        -r <root_folder>   : set root folder on S3.
        -i <input_file> [<input_file> ...] : list of input files or '-' for stdin
        -s <char>          : replace default separator '§' with <char>.
        -w                 : overwrite existing target files.
        -k <max_seconds>   : set minimal age (in seconds) for files to be processed.
        -o <output_file>   : set an output file (default is stdout/stderr).
        -h                 : show this help message
        --help             : show full help
        -v                 : show program's version
    
    Ex. : prog.py -b finance-depart-bucket -r customer_invoices/2025/01 -i rename.lst rename1.lst rename2.lst -s@ 
                  -o ren_invoices_2025_Jan.log -k 3600 -w
    
      Process files in s3://finance-depart-bucket/customer_invoices/2025/01/ (-b/-r) that haven't changed for 1h (-k) overwrting 
      existing files (if any, -w) and trace all operations to "ren_invoices_2025_Jan.log" (-o)

### Example use
The example at the end of the short help above comes from a new argument `example_use` to `ArgumentParser` :
```python
argparse.ArgumentParser( .. , example_use='''
Ex. : %(prog)s@FI@ -b finance-depart-bucket -r customer_invoices/2025/01 -i rename.lst rename1.lst rename2.lst -s@
-o ren_invoices_2025_Jan.log -k 3600 -w
@NL@
  Process files in s3://finance-depart-bucket/customer_invoices/2025/01/ (-b/-r) that haven't changed for 1h (-k)
  overwrting existing files (if any, -w) and trace all operations to "ren_invoices_2025_Jan.log" (-o)
''', .. )
```
This new argument is formatted exactly like help strings, and enjoys the forced line breaks with the help of `@NL@` tags + one more special tag : `@FI@` that you can customize like this : `argparse.ArgumentParser(.. , indent_pick='@IndentHere@', .. )` (inserted after `%(prog)s` in the example above).

The effect of `@FI@` (Following Indent) : all following lines shall be indented to this position (where the tag appears).

This effect ceases at the first `@NL@` encountered ! (so you can regain some control)

This can take a little trial and error until you get the exact format you want, but an `example_use` is intended for `short_help`, so it shouldn't be that hard to try it on a couple of lines.

It is worth it though, to get a pretty usage example. Compare neatly indented usage :

    Ex. : prog.py -b finance-depart-bucket -r customer_invoices/2025/01 -i rename.lst rename1.lst rename2.lst -s@
                  -o ren_invoices_2025_Jan.log -k 3600 -w
to

    Ex. : prog.py -b finance-depart-bucket -r customer_invoices/2025/01 -i rename.lst rename1.lst rename2.lst -s@
    -o ren_invoices_2025_Jan.log -k 3600 -w
Also : the formatter tries to take a hint from an initial indentation at the beginning of the first line or just after an `@NL@` tag :
```python
argparse.ArgumentParser( .. , example_use='''
...
@NL@
  Process files ...
''', .. )
```
Notice how the indentation of 'Process files .. ' is preserved in the formatted output above.

---------------

This is published under [Python License](https://github.com/python/cpython/blob/main/LICENSE "Strikethrough").

Please open an issue for any encountered bugs, or report to wj.osprojects@gmail.com

