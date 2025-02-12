#!/bin/csh

set prog = `basename $0`

echo "[${prog}] INFO (`date +'%m/%d/%Y %H:%M:%S'`) ${prog} started"
set st_tot = `date +'%s'`

# Load tool if needed

setenv VCS_STOP_SAFE         1

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

setenv LICENSE_WAIT_TIME 1

#clean up
rm -f sv_files.f vlog.log dpi.f shlib_file.f elab.log

#------------------
# prepare listfile
#------------------
set filelist = "sv_files.f"
set st       = `date + '%s'`
set proc     = "vcs-vlog (vips)"

echo "[${prog}] INFO (`date +'%m/%d/%Y %H:%M:%S'`) starting ${proc}"

vlogan \
  -Mdir=csrc \
  -full64 \
  -q \
  +define+SYNOPSYS \
  +define+SNPS \
  +define+VCS \
  +define+VCSMX \
  -sverilog \
  +libext+.v+.vh+.sv+.svh+.vp+.svp+.bv+.vs+.prv \
  +systemverilogext+.v+.vh+.sv+.svh+.vp+.svp+.bv+.vs+.prv \
  +lint=CDOB,ERASM,PCWM,PCWM-L,TFIPC,TFIPC-L,TFIPCI-L \
  -suppress=SV-LCM-PPWI \
  +warn=all,noDRTZ,noLCA_FEATURES_ENABLE,noMCFNF,noVCM-HFUFR,noVCM-TRIMVEC \
  -error=DPIMI,noMPD,PCWM-W,SFDCOM-CNOF,TFIPC,TNR \
  +error+2 \
  -assert svaext \
  -kdb \
  +define+XPROP \
  +define+VPD \
  +define+FSDB_SUPPORT \
  -f ${filelist} \
  -l vlog.log

set exit_code = $?
set et = `date +'%s'`

if ( $exit_code ) then
  echo "[${prog}] ERROR (`date +'%m/%d/%Y %H:%M:%S'`) ${proc} exited with code ${exit_code} (duration=`${SIM_ROOT}/bin/timediff $st $et`)"
  exit ${exit_code}
endif

echo "[${prog}] INFO (`date +'%m/%d/%Y %H:%M:%S'`) ${proc} completed successfully (duration=`${SIM_ROOT}/bin/timediff $st $et`)"


set filelist = ""
set st       = `date + '%s'`
set proc     = "vcs-elab"

echo "[${prog}] INFO (`date +'%m/%d/%Y %H:%M:%S'`) starting ${proc}"

vcs \
  -licwait 1 \
  -Mdir=csrc \
  -o simv \
  -full64 \
  -q \
  -l elab.log \
  -reportstats \
  +noportcoerce \
  +lint=CDOB,ERASM,PCWM,PCWM-L,TFIPC,TFIPC-L,TFIPCI-L \
  -suppress=SV-LCM-PPWI \
  +warn=all,noDRTZ,noLCA_FEATURES_ENABLE,noMCFNF,noVCM-HFUFR,noVCM-TRIMVEC \
  -suppress=SV-LCM-PPWI \
  +warn=all,noDRTZ,noLCA_FEATURES_ENABLE,noMCFNF,noVCM-HFUFR,noVCM-TRIMVEC \
  -error=DPIMI,noMPD,PCWM-W,SFDCOM-CNOF,TFIPC,TNR \
  +error+2 \
  -xprog=xprog.cfg \
  -kdb \
  -cm line+branch+tgl+cond+fsm+assert \
  -cm_cond event \
  -diag noconst \
  -cm_noconst \
  -cm_seqnoconst \
  -cm_libs yv+celldefine \
  -cm_hier cm_hier \
  -add_seq_delay 1ps \
  +nospecify \
  -CFLAGS -m64 \
  -CFLAGS -std=c99 \
  -LDFLAGS "-lm" \
  -CFLAGS -DSYNOPSYS \
  -CFLAGS -DSNPS \
  -CFLAGS -DVCS \
  -CFLAGS -DVCSMX \
  -file dpi.f \
  -debug_access+all \
  -debug_region+cell+encrypt \
  -top def_clk_prec \
  -top scope \
  -top scope \
  -top sim_pkg \
  -top sim_top \
  -top tb_top \
  -top test_pkg \
  -top uvm_custom_install_verdi_recording


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