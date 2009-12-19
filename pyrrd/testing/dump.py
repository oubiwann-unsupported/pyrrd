# This dump is from an rrd file with one data source and two RRAs.
simpleDump01 = """
<!-- Round Robin Database Dump --><rrd>  <version> 0003 </version>
  <step> 300 </step> <!-- Seconds -->
  <lastupdate> 920804400 </lastupdate> <!-- 1999-03-07 04:00:00 MST -->

  <ds>
    <name> speed </name>
    <type> COUNTER </type>
    <minimal_heartbeat> 600 </minimal_heartbeat>
    <min> NaN </min>
    <max> NaN </max>

    <!-- PDP Status -->
    <last_ds> UNKN </last_ds>
    <value> 0.0000000000e+00 </value>
    <unknown_sec> 0 </unknown_sec>
  </ds>

<!-- Round Robin Archives -->  <rra>
    <cf> AVERAGE </cf>
    <pdp_per_row> 1 </pdp_per_row> <!-- 300 seconds -->

    <params>
    <xff> 5.0000000000e-01 </xff>
    </params>
    <cdp_prep>
      <ds>
      <primary_value> 0.0000000000e+00 </primary_value>
      <secondary_value> 0.0000000000e+00 </secondary_value>
      <value> NaN </value>
      <unknown_datapoints> 0 </unknown_datapoints>
      </ds>
    </cdp_prep>
    <database>
      <!-- 1999-03-07 02:05:00 MST / 920797500 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:10:00 MST / 920797800 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:15:00 MST / 920798100 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:20:00 MST / 920798400 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:25:00 MST / 920798700 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:30:00 MST / 920799000 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:35:00 MST / 920799300 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:40:00 MST / 920799600 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:45:00 MST / 920799900 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:50:00 MST / 920800200 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:55:00 MST / 920800500 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:00:00 MST / 920800800 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:05:00 MST / 920801100 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:10:00 MST / 920801400 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:15:00 MST / 920801700 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:20:00 MST / 920802000 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:25:00 MST / 920802300 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:30:00 MST / 920802600 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:35:00 MST / 920802900 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:40:00 MST / 920803200 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:45:00 MST / 920803500 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:50:00 MST / 920803800 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:55:00 MST / 920804100 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 04:00:00 MST / 920804400 --> <row><v> NaN </v></row>
    </database>
  </rra>
  <rra>
    <cf> AVERAGE </cf>
    <pdp_per_row> 6 </pdp_per_row> <!-- 1800 seconds -->

    <params>
    <xff> 5.0000000000e-01 </xff>
    </params>
    <cdp_prep>
      <ds>
      <primary_value> 0.0000000000e+00 </primary_value>
      <secondary_value> 0.0000000000e+00 </secondary_value>
      <value> NaN </value>
      <unknown_datapoints> 0 </unknown_datapoints>
      </ds>
    </cdp_prep>
    <database>
      <!-- 1999-03-06 23:30:00 MST / 920788200 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 00:00:00 MST / 920790000 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 00:30:00 MST / 920791800 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 01:00:00 MST / 920793600 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 01:30:00 MST / 920795400 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:00:00 MST / 920797200 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 02:30:00 MST / 920799000 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:00:00 MST / 920800800 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 03:30:00 MST / 920802600 --> <row><v> NaN </v></row>
      <!-- 1999-03-07 04:00:00 MST / 920804400 --> <row><v> NaN </v></row>
    </database>
  </rra>
</rrd>
"""
