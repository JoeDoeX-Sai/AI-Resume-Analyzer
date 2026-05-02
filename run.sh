#!/bin/bash
# Quick start script for Linux/Mac

echo "Starting AI Resume Analyzer..."
echo ""

# Start backend
echo "Starting backend server..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend..."
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

# Wait a bit
sleep 2

# Open browser (try different commands for different systems)
echo "Opening browser..."
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:8000
elif command -v open > /dev/null; then
    open http://localhost:8000
else
    echo "Please open http://localhost:8000 in your browser"
fi

echo ""
echo "AI Resume Analyzer is running!"
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
