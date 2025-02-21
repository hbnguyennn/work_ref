#!/usr/bin/python3

import re, os, sys
import argparse

tcsection = {}
#-------------------------------------
# func : get_args
#-------------------------------------
def get_args():
   global args
   parser = argparse.ArgumentParser(
      prog = sys.argv[0],
      description = "gen full path of files base of files.f"
   )
   parser.add_argument("-i", "--input")
   parser.add_argument("-o", "--output")
   parser.add_argument("-c", "--cmd")
   args = parser.parse_args()
   #print (args.input)
   #print (args.output)
   #print (args.cmd)

def process_file(infile):
   f = open(infile, "r")
   section_cnt = 0

   for line in f:
      # refine lines
      line = line.replace("\n", "")    #remove line break
      line = re.sub(r'\s+',' ',line)   #remove unneccesery space
      line = re.sub(r'^\s+','',line)

      if not line.strip():          continue # Remove empty line
      if re.search(r'^\s*;', line): continue # Remove comment line (start with ";")

      if m := re.match(r'\[(\S+)\]', line): # start tcsection
         section_name = m.group(1)
         section_cnt  = section_cnt + 1
         #print (line + "---" + section_name)
         #if bool(re.match(r'regression.', section_name)):
         if section_name in tcsection:
            print ("ERROR: duplication section name [%s]" % section_name)
            exit(1)
         else :
            start_add_line = 1
            tcsection[section_name] = []
         #else:
         #   start_add_line = 0
      else:
         #if start_add_line:
            #print (line + "  " + section_name)
            tcsection[section_name].append(line)


   print (section_cnt)
   #print (tcsection["Default"])

   for sec in tcsection:
      print ('[' + sec + ']')
      for line in tcsection[sec]:
         print (line)
         if m := re.match(r'import\s*=\s*([\S+])', line):
            import_sec = m.group(1)
            #print (import_sec)
            if (import_sec in tcsection.keys()):
               lines = tcsection[import_sec]
               for line in lines:
                  print (line)
            #print(line, import_sec)


def main():
   get_args()

   process_file(args.input)

#-------------------
# calling main
#-------------------
if __name__ == '__main__':
   main()
else:
   pass