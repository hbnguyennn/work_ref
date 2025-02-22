#!/usr/bin/python3

import re, os, sys
import argparse
import pprint

GL_TCSECTIONS = {}

re_import   = re.compile(r'import\s*=\s*(\S+)')

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

#-------------------------------------
# func : parser_import
#-------------------------------------
def parser_import(section, curr_sec):
   #print("Calling parser_import" + section + " - " + curr_sec)
   if section in GL_TCSECTIONS.keys():
      for line in GL_TCSECTIONS[section]["LINES"]:
         import_m = re_import.match(line)
         if import_m:
            parser_import(import_m.group(1), curr_sec)
         else :
            if not GL_TCSECTIONS[curr_sec]["LINES"]:
               GL_TCSECTIONS[curr_sec]["LINES"] = []

            GL_TCSECTIONS[curr_sec]["LINES"].append(line)
   else :
      print ("ERROR: %s is not valid" % section)

#-------------------------------------
# func : convert_table_to_list
#-------------------------------------
def convert_table_to_list(table):
   results   = []
   n_results = []
   len_row   = len(table)
   len_col   = len(table[0])

   #-------------------#
   # handle 1st column #
   #-------------------#
   for row in range(len_row):
      item = table[row][0]
      if item :
         if item == '-':
            print ("ERROR: '-' should not be in first column!")
            exit (1)
         else :
            results.append(item)
   #----------------------#
   # handle others column #
   #----------------------#
   for col in range(1,len_col):
      for row in range(len_row):
         item = table[row][col]
         if item :
            if item == '-':
               for prefix in results :
                  if prefix not in n_results :
                     n_results.append(prefix)
            else :
               for prefix in results :
                  n_results.append(f"{prefix}.{item}")

      results = n_results.copy()
      n_result=[]

   results = sorted(list(dict.fromkeys(results)), key=lambda x: x[0])
   pprint.pprint(results)
   print (f"Total tests: {len(results)}")

#-------------------------------------
# Process input file
# Create TC database
#-------------------------------------
def process_file(infile):
   f = open(infile, "r")
   section_cnt = 0

   for line in f:
      # refine lines
      line = line.replace("\n", "")          # Remove line break
      line = re.sub(r'\s+',' ',line)         # Remove unneccesery space
      line = re.sub(r'^\s+','',line)         # Remove starting space
      line = re.sub(r';;.*','',line)         # Remove comment line (start with ;;)
      if not line.strip():          continue # Remove empty line
      if re.search(r'^\s*;', line): continue # Remove comment line (start with ";")

      if m := re.match(r'\[(\S+)\]', line): # start GL_TCSECTIONS
         section_name = m.group(1)
         section_cnt  = section_cnt + 1
         if section_name in GL_TCSECTIONS:
            print ("ERROR: duplication section name [%s]" % section_name)
            exit(1)
         else :
            # Initial section and section->lines_list
            GL_TCSECTIONS[section_name] = {}
            GL_TCSECTIONS[section_name]["LINES"] = []
      else:
         GL_TCSECTIONS[section_name]["LINES"].append(line)

   # Debug
   if 0 :
      for section in GL_TCSECTIONS.keys():
         print (section)
         for line in GL_TCSECTIONS[section]["LINES"]:
            print (line)

      exit(1)

   #-----------------------------
   # parser each section lines
   #-----------------------------
   for sec in GL_TCSECTIONS:
      section = GL_TCSECTIONS[sec]
      lines   = section["LINES"]

      section["HAS_TABLE"] = 0
      #--------------------------
      # process import = xxxx
      #--------------------------
      for line in lines:
         m_import   = re_import.match(line)
         if m_import:
            parser_import(m_import.group(1), sec)
            lines.remove(line)

      #--------------------------------
      # process property AAAA = BBBBB
      #--------------------------------
      #lines       = section["LINES"]
      re_property = re.compile(r'(\S+)\s*=\s*(\S+)')
      for line in lines:
         m_property = re_property.match(line)
         if m_property:
            name  = m_property.group(1)
            value = m_property.group(2)
            if section.get("PROPERTIES") is None:
               section["PROPERTIES"] = {}
               properties = section["PROPERTIES"]

            properties[name] = value
            # FIXME : How to remove current processed line
         else : # work around
            if section.get("RLINES") is None:
               section["RLINES"] = []
               rline = section["RLINES"]
            rline.append(line)

      #--------------------------
      # process tc table
      #--------------------------
      if rline is not None:
         start_table      = 0
         table_cnt        = 0
         for line in rline:
            if re.match(r'\+--\S+', line):
               start_table += 1;
               if start_table == 1:
                  if section.get("TABLES") is None:
                     section["TABLES"] = {}
                     tables = section["TABLES"]
                  table_cnt += 1
            if re.match(r'^\s*\|\s*\S+', line):
               if tables.get("TABLE" + str(table_cnt)) is None:
                  tables["TABLE" + str(table_cnt)] = []
                  table = tables["TABLE" + str(table_cnt)]
                  section["HAS_TABLE"] = 1
               start_table = 0
               line  = re.sub(r'\s+',     '', line) # Remove all space
               line  = re.sub(r'^\|',     '', line) # remove first '|'
               line  = re.sub(r'\|\s*$',  '', line) # remove last  '|'
               items = line.split('|')
               table.append(items)

   #--------------------------
   # clean up
   #--------------------------
   for sec in GL_TCSECTIONS:
      section = GL_TCSECTIONS[sec]
      lines   = section["LINES"]
      if lines is not None:
         del section["LINES"]

      if section.get("RLINES") is not None:
         rlines  = section["RLINES"]
         # FIXME : might need to take care of line is not process
         del section["RLINES"]

   # Test
   if 1:
      print("DB---------------------")
      #pprint.pprint(GL_TCSECTIONS["Default"]["TABLES"])
      table = GL_TCSECTIONS["Default"]["TABLES"]["TABLE1"]
      #table = GL_TCSECTIONS["blocks"]["TABLES"]["TABLE1"]
      #table = GL_TCSECTIONS["test_traffic_random"]["TABLES"]["TABLE1"]
      convert_table_to_list(table)
      #pprint.pprint(table)
      #pprint.pprint(GL_TCSECTIONS["tests"]["TABLES"])
      #pprint.pprint(GL_TCSECTIONS["regressions"]["TABLES"])
      #pprint.pprint(GL_TCSECTIONS["test_table"])
      #pprint.pprint(GL_TCSECTIONS["imp_test_1"])
      #pprint.pprint(GL_TCSECTIONS["Default"])
      print("DB---------------------")

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