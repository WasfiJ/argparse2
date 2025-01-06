
# Example use for argparse2

import argparse2 as argparse

__ver = '0.6'; __lupdate = '2022.01.05'

sep = '§'
NoClobber = True
MIN_AGE = 40 # seconds

# Program to mass move/rename files in a given folder in an S3 bucket
prog='aws_mass_mv.py'

action='action'; opts='opts'; dest='dest'; meta='metavar'; desc='desc'; help='help'; version='version'; nargs='nargs'; typ='type'
nMax='max_use_count'; nMaxErr='max_use_err'; required='required'; recommend='recommend'; deprecated='deprecated'; default='default'

# General setup
Args= { 
  # Remote location
  'b' : { opts: ['-b', '--bucket'],                  dest: 'bucket',  meta: '<Bucket>',      nargs: 1,   required: True               },
  'r' : { opts: ['-r', '--root'],                    dest: 'root',    meta: '<root_folder>', nargs: 1,   required: True               },
  # Input                                                                                                                            
  'i' : { opts: ['-i', '-in', '--input'],            dest: 'input',   meta: '<input_file>',  nargs: '+', required: True               },
  's' : { opts: ['-s', '--separator'],               dest: 'sep',     meta: '<char>',        nargs: 1,   default: [sep]               },
  # Behaviour                                                                                                          
  'k' : { opts: ['-k', '--skip-recent'],             dest: 'age',     meta: '<seconds>',     nargs: 1,   recommend: True,
          default: [MIN_AGE], typ: int },
  'w' : { opts: ['-w', '--overwrite', '--clobber'],  dest: 'clobber',      action: 'store_true'                                       },
  # Misc                                                                                                                             
  'o' : { opts: ['-o', '-out', '--out'],             dest: 'outF',    meta: '<output_file>', nargs: 1                                 },

   'h' : { opts: ['-h'],                     action: 'short_help' },
  'hh' : { opts: ['--help', '--full-help'],  action: 'help'       },
   'v' : { opts: ['-v', '--version'],        action: 'version'    }
}

# Help/desc strings (and custom error messages)
ArgTexts = {
  'b' : { desc: '%(help)s', help: 'Set S3 bucket.',
          nMax: 1, nMaxErr: '\n  Please provide one single S3 bucket !'  },
  
  'r' : { desc: '%(help)s', help: 'Set root folder on S3.' },
  
  'i' : { desc: "list of input files or '-' for stdin", help:"'-' for stdin or a list of files (which will be processed in order)." },
  
  's' : { desc: '%(help)s', help: "Replace default separator '"+sep+"' with <char>.",
          nMax: 1, nMaxErr: '\n  Please provide one single separator for input data !\n'  },
  
  'w' : { desc: 'overwrite existing target files.',
          help: 'Default : no overwrite (skip existing target files).@NL@If set : overwrite an existing [dstFileName] (at your own risks !).' }, 
  
  'k' : { desc: 'set minimal age (in seconds) for files to be processed.', 
          help:'Default is to skip files modified less than %ds ago.@NL@\
          If set : skip files not older than <max_seconds> seconds. Adjust to your specific situation.@NL@\
          Set to 0 to disable (at your own risks !). Note that even in this case if ETag changes\
          during the copy operation, the file will still be skipped (it is being actively modified !).' %MIN_AGE },
  
  'o' : { desc: '%(help)s', help: "Set an output file (default is stdout/stderr).",
          nMax: 1, nMaxErr: '\n  Please provide one single output target !\n'         },
  
   'h' : { desc: 'show this help message', help: 'Show short help message and exit.' },
  'hh' : { desc: 'show full help',         help: 'Show this help message and exit.' },
   'v' : { desc: "show program's version", help: "Show program's version number and exit.", 
           version: '%(prog)s v'+__ver+' ('+__lupdate+')@NL@Please report any issues to wj.osprojects@gmail.com'   }
}

# Program description & example use
description = '''

  Rename/move files inside a folder in S3.

             ---------------------------------------------------------------------

Input format : (parsed as UTF-8)

         srcPath § dstPath § srcFileName § dstFileName
 
 * dstPath & dstFileName can be '=', which means srcPath == dstPath / srcFileName == dstFileName.
 * '-' for srcPath means : inherit from previous line. No inheritance for dstPath & filenames.

 Example :

   folder1 § =       § old0.txt § new0.txt  <<< srcPath == dstPath == [Bucket/root_folder/]folder1
   -       § =       § old1.txt § new1.txt  <<< folder name "sticks" from previous line
   folder2 § =       § old2.txt § new2.txt  <<< operating in a new folder : rename inside 'folder2'
   -       § folder3 § old3.txt § =         <<< move 'old3.txt' from 'folder2' (inherited) to 'folder3'

             ---------------------------------------------------------------------
'''

example_use='''
Ex. : %(prog)s@FI@ -b finance-depart-bucket -r customer_invoices/2025/01 -i rename1.lst rename2.lst -s@
                   -o ren_invoices_2025_Jan.log -k 3600 -w
@NL@
  Process files in s3://finance-depart-bucket/customer_invoices/2025/01/ (-b/-r) as per rename1.lst & rename2.lst (-i) with @ separator (-s)
  that haven't changed for 1h (-k) overwrting existing files (if any, -w) and trace all operations to "ren_invoices_2025_Jan.log" (-o)
'''

# Helper function
def add_argument(parser, opts) :
  global default_action
  for opt in opts :
    kwArgs = {}
    d = ArgTexts[opt]
    for arg in [help, desc, version, nMax, nMaxErr] :
      if arg in d : kwArgs[arg] = d[arg]
    d = Args[opt]
    if action in d : kwArgs[action] = d[action]
    else : kwArgs[action] = default_action
    for arg in [dest, nargs, required, recommend, deprecated, default, typ, meta] :
      if arg in d : kwArgs[arg] = d[arg]
    parser.add_argument( *d['opts'], **kwArgs )

# Main parser with epilog
parser = argparse.ArgumentParser(prog=prog, add_help=False, description=description, example_use=example_use,
 formatter_class=argparse.ArgumentQualifHelpFormatter, width=136, raw_description=True, error_tag='  !! Error',  
 epilog="Please report any issues to wj.osprojects@gmail.com"  
)

default_action = 'extend' # default action for all arguments
add_argument( parser.add_argument_group('== Remote location '), ['b','r'] )
add_argument( parser.add_argument_group('== Input '),           ['i','s'] )
add_argument( parser.add_argument_group('== Behaviour '),       ['w','k'] )
add_argument( parser.add_argument_group('== Misc. '),           ['o','h','hh','v'] )

args = parser.parse_args()

# -b finance-depart-bucket -r customer_invoices/2025/01 -i rename.lst rename1.lst rename2.lst -s@ -w
#   bucket=['finance-depart-bucket'], 
#   root=['customer_invoices/2025/01'], 
#   input=['rename.lst', 'rename1.lst', 'rename2.lst'],
#   sep=['§', '@'],
#   clobber=True,
#   age=[40], outF=None
bucket = args.bucket[0]
s3RootDir = args.root[0]
if args.sep and len(args.sep)>1 : sep = args.sep[1]     # len > 1 because there is a default
if args.age and len(args.age)>1 : MIN_AGE = args.age[1]
NoClobber = False if args.clobber else True
outF = args.outF[0] if args.outF else None
inputs = args.input

def print_global_entities(collection):
  for k, v in globals().items(): 
    if k in collection : print(f"{k:>15s} = {v}")

print_global_entities(('bucket','s3RootDir','NoClobber','MIN_AGE','sep','outF', 'inputs'))

raise SystemExit(0)
