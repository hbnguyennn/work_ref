#!/usr/bin/python3

import re, os, sys
import argparse
import pprint

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
# Process input file
#-------------------------------------
def process_file(infile, ofile, debugfile):
   for file in infile:
      f = open(file, "r")
      lineno = 0
      disable_output = 0
      for line in f:
         has_svpp_prefix    = 0
         has_svpp_directive = 0

         lineno += 1;
         line = line.replace("\n", "")          # Remove line break
         print (f"{lineno} {line}");

         if re.search(r'@@\S+', line):
            print (f"[ERROR]: missing space following @@ {file}:{lineno}")
            exit(1)
         if m := re.match(r'@@\s+kpp\s+(\S+)', line, re.IGNORECASE) :
            print (f"have directive : {m.group(1)}")
            if re.search(r'translate_off',m.group(1), re.IGNORECASE):
               disable_output = 1
               print ("disable output")
            elif re.search(r'translate_on',m.group(1), re.IGNORECASE):
               disable_output = 0
               print ("enable output")
         elif re.search(r'@@\s+kpp\s*$', line, re.IGNORECASE) :
            print(f"[ERROR]: nothing following kpp directive @@ {file}:${lineno}")
            exit (1)
         elif re.search(r'@@\s+#\s*kpp\s*$', line, re.IGNORECASE) :
            print(f"[INFO]: comment line @@ {file}:${lineno}")
            exit (1)





#-------------------------------------
# func : main
#-------------------------------------
def main():
   get_args()
   process_file(args.input, args.output, args.debugfile)
   #process_cmd(args.cmd)

#-------------------
# calling main
#-------------------
if __name__ == '__main__':
   main()
else:
   pass