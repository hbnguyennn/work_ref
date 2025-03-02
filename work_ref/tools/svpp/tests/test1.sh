#!/bin/sh

TESTDIR="${srcdir}/tests"
TESTNAME="test1"
RESULT="/tmp/${TESTNAME}.results$$"

./kpp -o ${RESULT} ${TESTDIR}/${TESTNAME}.kpp

cmp ${RESULT} ${TESTDIR}/${TESTNAME}.expected_results

EXITCODE=$?

if [ "$EXITCODE" -eq 0 ]; then
   rm -f ${RESULT}
fi

exit ${EXITCODE}