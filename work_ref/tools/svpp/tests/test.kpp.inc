my @testconfg = (
  #  direction      name                     type                    default
  ["dec|enc",       "cfg_operation_mode",    "rvc_cfg_uint#(32)",    "1"                   ],
  ["enc",           "cfg_debug_mode",        "rvc_cfg_uint#(32)",    "0~1"                 ],
  ["dec",           "cfg_debug_mode",        "rvc_cfg_uint#(32)",    "0~1"                 ],
  ["dec|enc",       "cfg_debug_mode",        "rvc_cfg_uint#(32)",    "0~1"                 ],
  ["dec|enc",       "cfg_debug_mode",        "rvc_cfg_uint#(32)",    "0~1"                 ],
);

sub direction {my $a = shift; return $a->[0];}
sub name      {my $a = shift; return $a->[1];}
sub cfg_type  {my $a = shift; return $a->[2];}
sub default   {my $a = shift; return $a->[3];}

sub var_declare {
   my $indent = shift;
   my $ret    = "";
   my $fmt    = << "END_OF_STR";
$indent// Variable: %s_%s
$indent// default value : %s
$indent%s %s;

END_OF_STR

   foreach my $list (@testconfg) {
      my $r_dir = direction($list);
      if    ($r_dir eq 'dec'){ $r_dir = "rx";}
      elsif ($r_dir eq 'enc'){ $r_dir = "tx";}
      else                   { $r_dir = "glb";}

      $ret .= sprintf $fmt, $r_dir, name($list), default($list), cfg_type($list), name($list);
   }
   return $ret;
}

#print(var_declare("   "));
