#!/bin/sh

# Enhanced MARTZK Decipher Script with Auto-Resolution

# Initialize variables
requester_name=""
message_id=""
slice_id=""
output_folder=""

# Parse command-line arguments
while [ $# -gt 0 ]; do
    key="$1"
    case $key in
        --requester_name|-r)
            requester_name="$2"
            shift 2
            ;;
        -m|--message_id)
            message_id="$2"
            shift 2
            ;;
        -s|--slice_id)
            slice_id="$2"
            shift 2
            ;;
        -o|--output_folder)
            output_folder="$2"
            shift 2
            ;;
        *)
            echo "Unknown option $1"
            exit 1
    esac
done

# Input validation
if [ -z "$requester_name" ] || [ -z "$message_id" ] || [ -z "$output_folder" ]; then
    echo "Error: Missing required parameters"
    exit 1
fi

if [ ! -d "$output_folder" ]; then
    echo "Error: Output folder does not exist: $output_folder"
    exit 1
fi

# Auto-resolve aliases
if [ "$message_id" = "last_message_id" ]; then
    if [ -f "../src/.cache" ]; then
        actual_message_id=$(grep "message id:" ../src/.cache | tail -1 | awk '{print $3}')
        if [ -n "$actual_message_id" ]; then
            message_id="$actual_message_id"
            echo "Resolved 'last_message_id' to: $message_id"
        else
            echo "Error: Could not resolve 'last_message_id'"
            exit 1
        fi
    else
        echo "Error: Cache file not found"
        exit 1
    fi
fi

# Auto-resolve slice aliases
if [ -n "$slice_id" ] && [ -f "../src/.cache" ]; then
    case "$slice_id" in
        slice1)
            actual_slice_id=$(grep "slice1$" ../src/.cache | tail -1 | awk '{print $5}')
            ;;
        slice2) 
            actual_slice_id=$(grep "slice2$" ../src/.cache | tail -1 | awk '{print $5}')
            ;;
        slice3)
            actual_slice_id=$(grep "slice3$" ../src/.cache | tail -1 | awk '{print $5}')
            ;;
        slice4)
            actual_slice_id=$(grep "slice4$" ../src/.cache | tail -1 | awk '{print $5}')
            ;;
        *)
            actual_slice_id="$slice_id"
            ;;
    esac
    
    if [ -n "$actual_slice_id" ] && [ "$actual_slice_id" != "$slice_id" ]; then
        slice_id="$actual_slice_id"
        echo "Resolved slice alias to: $slice_id"
    fi
fi

echo "Initiating MARTZK decryption process..."

# Build command
reader_command="python3 ../src/reader.py --message_id \"$message_id\" --reader_name \"$requester_name\" --output_folder \"$output_folder\""

if [ -n "$slice_id" ]; then
    reader_command="$reader_command --slice_id \"$slice_id\""
fi

echo "Executing: $reader_command"
eval $reader_command

if [ $? -ne 0 ]; then
    echo "Error: Decryption process failed."
    exit 1
else
    echo "[SUCCESS] Decryption process completed successfully."
fi