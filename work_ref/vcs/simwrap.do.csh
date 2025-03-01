#!/bin/csh

set prog = `basename $0`

echo "[${prog}] INFO (`date +'%m/%d/%Y %H:%M:%S'`) ${prog} started"
set st_tot = `date +'%s'`

# Load tool if needed

setenv VERDI_VERSION verdi/2023
eval 'module unload verdi'          >& /dev/null
eval 'module load ${VERDI_VERSION}' >& /dev/null

setenv VCS_STOP_SAFE          1
setenv VCS_LIC_EXPIRE_WARNING 0

if ( ${?VERDI_HOME} ) then
  if ( ${?LD_LIBRARY_PATH})) then
    setenv LD_LIBRARY_PATH ${VERDI_HOME}/share/PLI/lib/LINUX64:${LD_LIBRARY_PATH}
  else
    setenv LD_LIBRARY_PATH ${VERDI_HOME}/share/PLI/lib/LINUX64
  endif
endif

setenv UVM_HOME ${VERDI_HOME}/etc/uvm-1.2

if ( -d ${UVM_HOME}/src ) then
  setenv UVM_SRC ${UVM_HOME}/src
else
  setenv UVM_SRC ${UVM_HOME}
endif

#clean up
rm -f sim.log

set st       = `date + '%s'`
set proc     = "vcs-sim"

echo "[${prog}] INFO (`date +'%m/%d/%Y %H:%M:%S'`) starting ${proc}"

/path_to_simv/simv \
  -licwait 1 \
  -l sim.log \
  -reportstats \
  +UVM_NO_RELNOTES \
  -suppress=SV-LCM-PPWI \
  +warn=noLCA_FEATURE_ENABLE \
  -error=SDFCOM_CNOF \
  -assert nopostproc \
  -cm line+branch+tgl+cond+fsm+assert \
  -cm_name test_name \
  -cm_log /dev/null \
  +seed=1231231 \
  +ntb_random_seed=1231231 \
  +test=test_name \
  +UVM_MAX_QUIT_COUNT=2 \
  -f plusargs.f \
  +UVM_VERBOSITY=UVM_MEDIUM

set exit_code = $?
set et = `date +'%s'`

if ( $exit_code ) then
  echo "[${prog}] ERROR (`date +'%m/%d/%Y %H:%M:%S'`) ${proc} exited with code ${exit_code} (duration=`${SIM_ROOT}/bin/timediff $st $et`)"
  exit ${exit_code}
endif

echo "[${prog}] INFO (`date +'%m/%d/%Y %H:%M:%S'`) ${proc} completed successfully (duration=`${SIM_ROOT}/bin/timediff $st $et`)"

set et_tot = `date +'%s'`
echo "[${prog}] INFO (`date +'%m/%d/%Y %H:%M:%S'`) ${prog} completed (duration=`${SIM_ROOT}/bin/timediff $st $et`)"

exit 0
