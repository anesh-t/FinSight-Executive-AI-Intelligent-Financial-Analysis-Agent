#!/bin/bash

# Run all 8 tests one by one with pause between each
# Usage: bash run_all_tests.sh

echo "================================================================================"
echo "RUNNING ALL 8 UNSTRUCTURED TESTS"
echo "================================================================================"
echo ""
echo "This will run 8 tests with a 2-second pause between each"
echo "Press Ctrl+C to stop at any time"
echo ""
sleep 2

for i in {1..8}; do
    echo ""
    echo "################################################################################"
    echo "# TEST $i/8"
    echo "################################################################################"
    echo ""
    
    python test_one_by_one.py $i
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  Test $i failed or was interrupted"
    fi
    
    if [ $i -lt 8 ]; then
        echo ""
        echo "⏸️  Pausing 2 seconds before next test..."
        sleep 2
    fi
done

echo ""
echo "================================================================================"
echo "ALL TESTS COMPLETE"
echo "================================================================================"
