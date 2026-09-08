#!/bin/bash
# Step 5: Validation testing
# Run the subscriber in one terminal, then the two publisher commands
# in another to observe allow vs. silent-deny behavior.
#
# Set OT_OPERATOR_PW and SENSOR_NODE_PW before running, e.g.:
#   export OT_OPERATOR_PW='change-me'
#   export SENSOR_NODE_PW='change-me'

CAFILE=/etc/mosquitto/certs/ca.crt

echo "--- Subscriber (ot_operator, broad read) ---"
echo "mosquitto_sub -h localhost -p 8883 --cafile $CAFILE -t '#' -u ot_operator -P \$OT_OPERATOR_PW -v"

echo ""
echo "--- Publisher (sensor_node, allowed topic) ---"
echo "mosquitto_pub -h localhost -p 8883 --cafile $CAFILE -t 'factory/sensor/temperature' -m '24.1C' -u sensor_node -P \$SENSOR_NODE_PW"

echo ""
echo "--- Publisher (sensor_node, denied control topic — expect SILENT drop, no client error) ---"
echo "mosquitto_pub -h localhost -p 8883 --cafile $CAFILE -t 'factory/control/plc1' -m 'STOP' -u sensor_node -P \$SENSOR_NODE_PW"
echo ""
echo "Confirm enforcement by checking the subscriber terminal — the STOP message should never appear."
