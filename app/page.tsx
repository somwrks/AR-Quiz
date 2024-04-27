'use client';

import React, { useState, useRef, useEffect } from 'react';
import Webcam from 'react-webcam';

const IndexPage: React.FC = () => {
  const webcamRef = useRef<Webcam>(null);
  const [lifeline, setLifeline] = useState(3);
const [alert, setAlert] = useState("")
  const handleCapture = async () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        try {
          const response = await fetch('/api/detect_cheating', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageSrc.split(',')[1] }),
          });
          const data = await response.json();
          const {cheating_detected, lifeline: remainingLifeline } = data;
          setLifeline(remainingLifeline);
          console.log(cheating_detected)
          if (cheating_detected==1) {
            setAlert('Cheating detected! You have lost a lifeline.');
          } else{
            setAlert(`You're clean!`);

          }
        } catch (error) {
          console.error('Error detecting cheating:', error);
        }
      }
    }
  };
  useEffect(() => {
    setTimeout(() => {
      handleCapture()
      console.log("sending requests")
    }, 1000);
    
  }, [])
  
  return (
    <div>
      <Webcam
        ref={webcamRef}
        width={640}
        height={480}
        screenshotFormat="image/jpeg"
      />
      {/* <button onClick={handleCapture}>Check for Cheating</button> */}
      <h1>{alert}</h1>
      <p>Lifeline: {lifeline}</p>
    </div>
  );
};

export default IndexPage;