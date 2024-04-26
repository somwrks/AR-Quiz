# Test Taking Website with Facial Recognition

## Overview
This project is a test-taking website with facial recognition to detect cheating behaviors. Users will be required to keep looking into the camera during the test, and if they look away or exhibit cheating behaviors, the test will be terminated. The project uses Next.js for the frontend, Flask for the backend, OpenCV/Mediapipe for facial recognition, and Supabase/Prisma for the database.

![image](https://github.com/somwrks/AR-Quiz/assets/85481905/49d4022f-0748-4e67-b8ab-895e30e82f54)


## Tech Stack
- Frontend:
  - Next.js
  - Tailwind CSS
  - React Webcam
- Backend:
  - Flask
  - OpenCV/Mediapipe
  - Prisma (interacting with Supabase)
- Database:
  - Supabase (PostgreSQL)

## Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/test-taking-website.git
   cd test-taking-website
2. Set up the backend:
    Create a virtual environment (optional but recommended)
    ```bash
    python -m venv venv
    source venv/bin/activate  # Activate the virtual environment
    ```
    Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
    Set up environment variables:
    Create a .env file based on .env.example and fill in the necessary credentials
    Run the Flask app:
    ```bash
    flask run
    ```
3. Set up the frontend:
   Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
   Install dependencies:
   ```bash
   npm install
   ```
   Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Access the website:
   Open your browser and go to http://localhost:3000 to access the test-taking website

## Project Structure
- `backend/`: Contains Flask backend code, including facial recognition logic.
- `frontend/`: Contains Next.js frontend code, including React Webcam integration.
- `database/`: Contains SQL scripts for setting up the database schema.
- `docs/`: Contains project documentation, including this README.md.

## Contributing
Feel free to contribute to this project by submitting pull requests. Make sure to follow the coding guidelines and provide clear commit messages.

## License
This project is licensed under the MIT License.
