#!/usr/bin/python3

import re, os, sys
import argparse

#-------------------------------------
# func : get_args
#-------------------------------------
def get_args():
   global args
   parser = argparse.ArgumentParser(
      prog = sys.argv[0],
      description = "gen full path of files base of files.f"
   )
   parser.add_argument("-i", "--input", action='append')
   parser.add_argument("-o", "--output")
   parser.add_argument("-d", "--debugfile")
   args = parser.parse_args()

#-------------------------------------
# create_header
#-------------------------------------
def create_header(df, ofile):
   df.write(f"use strict;\n")
   df.write(f"#use warning;\n")
   if ofile:
      df.write (f"open (my $OUTFILE, \">{ofile}\") ||\n")
      df.write (f"   die (\"ERROR: Unable to open {ofile}\\n\\n\");\n")
   else :
      df.write (f"my $OUTFILE = *STDOUT;\n")

#-------------------------------------
# create_footer
#-------------------------------------
def create_footer(df, ofile):
   if ofile:
      df.write (f"#\n");
      df.write (f"close($OUTFILE);\n")
      df.write (f"exit 0;\n")
   else :
      df.write (f"#\n")
      df.write (f"#\n")

   df.close()

#-------------------------------------
# Process input file
#-------------------------------------
def process_files(ifiles, ofile, dfile):

   df = open(dfile, "w")
   of = open(ofile, "w")

   lable_cnt = 0

   create_header(df, ofile)

   for file in ifiles:
      f = open(file, "r")

      df.write(f"#\n")
      df.write(f"# START OF FILE: {file}\n")
      df.write(f"#\n")

      lineno = 0
      state  = 0
      disable_output = 0
      for line in f:
         has_kpp_prefix    = 0
         has_kpp_directive = 0
         kpp_directive     = ""

         lineno += 1;
         line = line.replace("\n", "")          # Remove line break
         #print (f"{lineno} {line}");

         if re.search(r'@@\S+', line):
            print (f"[ERROR]: missing space following @@ {file}:{lineno}")
            exit(1)
         elif re.search(r'@@\s+\S+', line):
            has_kpp_prefix = 1
            line = line.replace('@@','')
         elif re.search(r'@@\s*$', line):
            continue
         else :
            has_kpp_prefix = 0

         if (has_kpp_prefix) :
            if re.search(r'\s+kpp\s*$', line, re.IGNORECASE) :
               print(f"[ERROR]: nothing following kpp directive @@ {file}:${lineno}")
               exit (1)
            elif re.search(r'\s+#\s*$', line, re.IGNORECASE) :
               #print(f"[INFO]: comment line @@ {file}:${lineno}")
               disable_output = 1
            elif m := re.match(r'\s+kpp\s+(\S+)$', line, re.IGNORECASE) :
               #print (f"have directive : {m.group(1)}")
               has_kpp_directive = 1
               kpp_directive = m.group(1)

         if has_kpp_directive:
            if re.search(r'translate_off',kpp_directive, re.IGNORECASE):
               disable_output = 1
               #print ("disable output")
            elif re.search(r'translate_on',kpp_directive, re.IGNORECASE):
               disable_output = 0
               #print ("enable output")
            elif re.search(r'perl_section_begin',kpp_directive, re.IGNORECASE):
               state = 2
            elif re.search(r'perl_section_end',kpp_directive, re.IGNORECASE):
               state = 0
            else :
               print (f"[ERROR] Unknown directive : {kpp_directive} @@  {file}:{lineno}")
               exit (1)
            df.write (f"#{line}\n")
         elif disable_output:
            df.write (f"#{line}\n")
         elif state == 0:
            if has_kpp_prefix:
               df.write (f"#{line}\n")
            else :
               label = f"KPP_LABEL_{lable_cnt}";
               lable_cnt += 1

               df.write (f"print $OUTFILE << {label}; # {lineno}\n")
               #df.write (f"{line}\n")
               print_modified_line(df, line)
               state = 1
         elif state == 1:
            if has_kpp_prefix:
               df.write (f"{label}\n")
               df.write (f"{line}\n")
               state = 0
            else :
               #df.write (f"{line}\n")
               print_modified_line(df, line)
         elif state == 2:
            df.write (f"{line}\n")
         elif state == 1:
            df.write (f"{line}\n")
      if state == 1:
         df.write (f"{label}\n")

      df.write(f"#\n")
      df.write(f"# END OF FILE: {file}\n")
      df.write(f"#\n")
      f.close()

   create_footer(df, ofile)


def print_modified_line(ifile, line):

   was_backlash = 0
   for idx, char in enumerate(line):
      if char == '\\':
         was_backlash = 1
         nxt_char == line[idx+1]
         if nxt_char == '@' or nxt_char == '$' or line[idx+2] == '{' :
            pass





   #ifile.write(f"{line}\n")

#-------------------------------------
# func : main
#-------------------------------------
def main():
   get_args()
   process_files(args.input, args.output, args.debugfile)

#-------------------
# calling main
#-------------------
if __name__ == '__main__':
   main()
else:
   pass