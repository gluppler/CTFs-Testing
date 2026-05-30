#!/bin/bash
# Usage: ./sliver_upload.sh <beacon_id> <local_file> <remote_path>
SESSION="sliver_up"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SLIVER_BIN="$SCRIPT_DIR/sliver-client_linux"
OUTFILE="/tmp/sliver_out.txt"

tmux kill-session -t "$SESSION" 2>/dev/null
sleep 0.3
tmux new-session -d -s "$SESSION" "$SLIVER_BIN console" 2>/dev/null
sleep 8
tmux send-keys -t "$SESSION" Enter
sleep 2

TARGET="$1"
FILE="$2"
REMOTE="$3"

tmux send-keys -t "$SESSION" "use $TARGET" Enter
sleep 2
tmux send-keys -t "$SESSION" "upload $FILE $REMOTE" Enter
sleep 20

tmux capture-pane -t "$SESSION" -p -S -20 > "$OUTFILE"
tmux send-keys -t "$SESSION" "exit" Enter
sleep 1
tmux kill-session -t "$SESSION" 2>/dev/null
perl -pe 's/\e\[[0-9;]*[a-zA-Z]//g; s/\e\][0-9;]*[^\a]*\a//g; s/\r\n/\n/g' "$OUTFILE"
