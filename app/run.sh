#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
BINARY="$DIR/bin/TPGammaL3Sim"
export ROOTSYS="$DIR/etc"
export LD_LIBRARY_PATH="$DIR/lib:$DIR/lib_root:$LD_LIBRARY_PATH"

if [ "$#" -eq 1 ]; then
    # Mode visu
    "$BINARY" "$1"
elif [ "$#" -ge 4 ]; then
    # Mode batch / sans visu
    "$BINARY" "$@"
else
    echo "Usage:"
    echo "  With visualization: $0 output_name"
    echo "  Without visualization: $0 output_name N_events macro ML_ON/OFF [N_threads if ML_ON]"
    exit 1
fi
