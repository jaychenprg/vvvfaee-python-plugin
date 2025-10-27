PORT=5000

PID=$(lsof -ti :$PORT)

if [ -n "$PID" ]; then
    echo "Stopping process $PID on port $PORT..."
    kill -9 $PID
    echo "Stopped."
else
    echo "No running vvvface-python-plugin process found on port $PORT."
fi
