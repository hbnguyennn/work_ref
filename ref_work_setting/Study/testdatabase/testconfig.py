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
   parser.add_argument("-b", "--block", action='append')
   parser.add_argument("-t", "--test",  action='append')
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
def convert_table_to_list(table, testname):
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
            if testname != '':
               item = testname + "." + item

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
   return results

#------------------------------------------
# gen_block_list from processed GL_TCSECTIONS
#------------------------------------------
def gen_block_list():
   blocks = GL_TCSECTIONS["blocks"]
   blocks["BLOCK_LISTS"] = []
   for table_idx in blocks["TABLES"]:
      table = blocks["TABLES"][table_idx]
      blocks["BLOCK_LISTS"] += convert_table_to_list(table, '')
   #pprint.pprint(blocks["BLOCK_LISTS"])

#------------------------------------------
# gen_test_list from processed GL_TCSECTIONS
#------------------------------------------
def gen_test_list():
   tests = GL_TCSECTIONS["tests"]
   tests["TEST_LISTS"] = {}
   testlist = tests["TEST_LISTS"]
   testcnt  = 1
   for table_idx in tests["TABLES"]:
      table = tests["TABLES"][table_idx]
      for row in range(len(table)):
         if row == 0:
            if table[row][1] is None or table[row][2] is None or table[row][3] is None:
               print("[ERROR] Feature/Owner/Feature is not specify in [tests]")
               exit (1)
            feature  = table[row][1]
            owner    = table[row][2]
            blocks    = []
            for jj in range(len(table)):
               if table[jj][3]:
                  item = table[jj][3].split(' ')
                  blocks += item

         testname = table[row][0]
         testlist["test_" + str(testcnt)] = {}
         test = testlist["test_" + str(testcnt)]
         test["name"]    = testname
         test["feature"] = feature
         test["owner"]   = owner
         test["blocks"]  = blocks
         testcnt += 1
   #pprint.pprint(testlist)
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
   if 0:
      print("DB---------------------")
      #pprint.pprint(GL_TCSECTIONS["Default"]["TABLES"])
      #table = GL_TCSECTIONS["Default"]["TABLES"]["TABLE1"]
      #table = GL_TCSECTIONS["blocks"]["TABLES"]["TABLE1"]
      #table = GL_TCSECTIONS["test_traffic_random"]["TABLES"]["TABLE1"]
      #table = GL_TCSECTIONS["rtl_signoff"]["TABLES"]["TABLE2"]
      #onvert_table_to_list(table)
      #pprint.pprint(table)
      #pprint.pprint(GL_TCSECTIONS["tests"]["TABLES"])
      #pprint.pprint(GL_TCSECTIONS["regressions"]["TABLES"])
      #pprint.pprint(GL_TCSECTIONS["test_table"])
      #pprint.pprint(GL_TCSECTIONS["imp_test_1"])
      #print.pprint(GL_TCSECTIONS["Default"])
      pprint.pprint(GL_TCSECTIONS["tests"])
      print("DB---------------------")
#-------------------------------------
# func : list_regrs
#-------------------------------------
def list_regrs():
   print ("#[INFO] Calling list-regr ....")
   RESULT = []
   for table_idx in GL_TCSECTIONS["regressions"]["TABLES"]:
      table = GL_TCSECTIONS["regressions"]["TABLES"][table_idx]
      for row in range(len(table)):
         RESULT.append(table[row][0])

   counter = 1
   for item in RESULT:
      print(f"[INFO] [reg {counter}] {item}")
      counter += 1
   print (f"[INFO] Total regression : {counter}")
#-------------------------------------
# func : list_regrs
#-------------------------------------
def list_tests(sel_blocks, sel_tests):
   RESULT = {}
   # Proccess TCBLOCKS and TCTESTS
   gen_block_list()
   gen_test_list()

   # Check if input is valid
   blocks = GL_TCSECTIONS["blocks"]["BLOCK_LISTS"]
   RESULT["BLOCKS"] = {}
   RESULT["TESTLISTS"] = []
   block_cnt     = 0
   for sel_block in sel_blocks:
      #print (sel_block)
      sel_block = re.sub('\*','.*', sel_block)
      sel_block = re.sub('\?','.', sel_block)
      block_pattern = r'^' + sel_block + r'$'
      block_match   = 0
      for block in blocks:
         if re.match(block_pattern,block):
            block_match = 1
            block_cnt  += 1
            #print(f"match {block} with pattern : {block_pattern} block_cnt : {block_cnt}")
            RESULT["BLOCKS"][str(f"block_{block_cnt}")] = {}
            RESULT["BLOCKS"][str(f"block_{block_cnt}")]["name"]       = block
            RESULT["BLOCKS"][str(f"block_{block_cnt}")]["sel_tests"]  = sel_tests
            RESULT["BLOCKS"][str(f"block_{block_cnt}")]["sel_blocks"] = sel_blocks

      if block_match == 0:
         print(f"[ERROR] '{sel_block}' is not valid!")
         print("Available blocks as below :")
         for item in blocks:
            print (f"   {item}")
         exit(1)
   #pprint.pprint(RESULT["BLOCKS"])

   #---------------------------------------
   # Find tests table need convert to list
   #---------------------------------------
   tests     = GL_TCSECTIONS["tests"]["TEST_LISTS"]
   #pprint.pprint(tests)
   for sel_test in sel_tests:
      if re.search(r'\.', sel_test):
         sel_testname,tmp = sel_test.split('.', 1)
      elif re.search(r'\*', sel_test):
         sel_testname,tmp = sel_test.split('*', 1)
         sel_testname += ".*"
      else :
         sel_testname = sel_test

      #print (f"sel_testname: {sel_testname}")
      test_pattern = r'^' + sel_testname + r'$'

      test_match = 0
      for test in tests:
         testname = tests[test]["name"]
         testblks = tests[test]["blocks"]
         if re.match(test_pattern,testname):
            test_match = 1
            for testblk in testblks:
               testblk = re.sub(r'\*', '.*', testblk)
               blk_pat = r'^' + testblk + r'$'
               for result_block in RESULT["BLOCKS"]:
                  result_block_name = RESULT["BLOCKS"][result_block]["name"]
                  if re.match(blk_pat, result_block_name):
                     #print (f"sel_testname [{sel_testname}] match test [{testname}] with testblock [{testblks}] in resultblk[{result_block_name}]")
                     if RESULT["BLOCKS"][result_block].get("basetestlists") is None:
                        RESULT["BLOCKS"][result_block]["basetestlists"] = []

                     if testname not in RESULT["BLOCKS"][result_block]["basetestlists"]:
                        RESULT["BLOCKS"][result_block]["basetestlists"].append(testname)
                     if testname not in RESULT["TESTLISTS"]:
                        RESULT["TESTLISTS"].append(testname)

      if test_match == 0:
         print(f"[ERROR] '{sel_test}' is not valid in block(s) {sel_blocks}")
         print("Available test as below :")
         for test in tests:
            testname = tests[test]["name"]
            print (f"   {testname}")
         exit(1)

   #pprint.pprint(RESULT)

   for section in RESULT["TESTLISTS"]:
      for idx in GL_TCSECTIONS[section]["TABLES"]:
         table = GL_TCSECTIONS[section]["TABLES"][idx];
         if RESULT.get("pretestlists") is None:
            RESULT["pretestlists"] = []
         RESULT["pretestlists"] += convert_table_to_list(table, section)

   #pprint.pprint(RESULT)

   for block in RESULT["BLOCKS"]:
      for sel_test in RESULT["BLOCKS"][block]["sel_tests"]:
         sel_test = re.sub('\*','.*', sel_test)
         test_pattern = r'^' + sel_test + r'$'
         for test in RESULT["pretestlists"]:
            if re.match(test_pattern, test):
               if RESULT["BLOCKS"][block].get("testlists") is None:
                  RESULT["BLOCKS"][block]["testlists"] = []
               if test not in RESULT["BLOCKS"][block]["testlists"]:
                  RESULT["BLOCKS"][block]["testlists"].append(test)

      #pprint.pprint(RESULT["BLOCKS"][block]["testlists"])
   for block in RESULT["BLOCKS"]:
      block_name = RESULT["BLOCKS"][block]["name"]
      for test in RESULT["BLOCKS"][block]["testlists"]:
         print(f"-b {block_name} -t {test}")


#-------------------------------------
# func : process_cmd
#-------------------------------------
def process_cmd(icmd):
   if re.match(r'list([-_]|)regr(ession|)', icmd):
      list_regrs()
   elif re.match(r'list([-_]|)test(s|)', icmd):
      if args.block is None:
         print("[ERROR] Need to input -b or -block for list-tests cmd")
         exit (1)
      if args.test is None:
         print("[ERROR] Need to input -t or -test for list-tests cmd")
         exit (1)

      list_tests(args.block, args.test)


#-------------------------------------
# func : main
#-------------------------------------
def main():
   get_args()
   process_file(args.input)
   process_cmd(args.cmd)

#-------------------
# calling main
#-------------------
if __name__ == '__main__':
   main()
else:
   pass