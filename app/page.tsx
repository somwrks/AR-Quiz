"use client";

import React, { useState, useRef, useEffect } from "react";
import Webcam from "react-webcam";
import { SignOutButton, useSignIn, useUser } from "@clerk/nextjs";
import { PrismaClient } from "@prisma/client";
import { SignIn } from "@clerk/nextjs";

const IndexPage: React.FC = () => {
  const { user } = useUser();
  const prisma = new PrismaClient();

  const webcamRef = useRef<Webcam>(null);
  const [testStarted, setTestStarted] = useState(false);
  const [index, setIndex] = useState<Number[]>([]);
  const [remainingLifeline, setRemainingLifeline] = useState(3);
  const [submit, setSubmit] = useState(false);
  const [questions, setQuestions] = useState<
    { text: string; answer: string[]; l: number }[]
  >([]);

  useEffect(() => {
    if (testStarted) {
      const interval = setInterval(() => {
        handleCapture();
      }, 3000);

      return () => clearInterval(interval);
    }
  }, [testStarted]);

  const handleStartTest = () => {
    setTestStarted(true);
    setRemainingLifeline(3);
    const temp = [
      {
        text: "What is 2+2?",
        answer: ["4", "2", "22", "44"],
        l: 0,
      },
      {
        text: "What is the color of blue?",
        answer: ["blue", "red", "yellow", "black"],
        l: 0,
      },
      {
        text: "We are here because...",
        answer: [
          "i don't know",
          "i don't know",
          "i don't know",
          "i don't know",
        ],
        l: 0,
      },
      {
        text: "Som is the coolest guy ever?",
        answer: ["Yes", "Yes", "Yes", "Yes"],
        l: 0,
      },
      {
        text: "OpenAi should hire som?",
        answer: ["Yes", "Yes", "Yes", "Yes"],
        l: 0,
      },
    ];
    // Assuming you have a way to populate the questions array
    setQuestions(temp);
  };

  const handleCapture = async () => {
    if (webcamRef.current) {
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc && submit==false) {
        setTimeout(async () => {
          
          try {
            const response = await fetch("/api/detect_cheating", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({ image: imageSrc.split(",")[1] }),
            });
            const data = await response.json();
            const { cheating_detected } = data;
            if (cheating_detected === 1 || cheating_detected === -1) {
              setRemainingLifeline(remainingLifeline - 1);
              setTimeout(() => {
                alert("Cheating detected! You have lost a lifeline.");
                
              }, 0);
              if (remainingLifeline === 0) {
                setTestStarted(false);
                setTimeout(() => {
                  alert("Take the test again, because you were cheating.");
                }, 0);
              }
            }
          } catch (error) {
            console.error("Error detecting cheating:", error);
          }
        }, 0);
        }
    }
  };
  const handleclick = (e: Number) => {
    setIndex((prevIndex) => [...prevIndex, e]);
  };
  const handleSubmit = async () => {
    setSubmit(true);
    try {
      console.log(user)
      const response = await fetch("/api/create-test-result", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: user?.username || "Anonymous",
          userId: user?.id || "123",
          score: index.length,
          livesLeft: remainingLifeline,
        }),
      });
      const data = await response.json();
      console.log(data.message);
    } catch (error) {
      console.error("Error creating test result:", error);
    }
  };



  const handleReset = ()=>{
    setIndex([])
    setTestStarted(false)
  }

  return (
    <div>
      <>
        {testStarted ? (
          <>
            <Webcam
              ref={webcamRef}
              width={640}
              height={480}
              screenshotFormat="image/jpeg"
            />
            <p>Lifeline: {remainingLifeline}</p>
            {questions.map((question, z) => (
              <div className="flex flex-col spacy-y-4" key={z}>
                <h2>{question.text}</h2>
                <div className="flex flex-row space-x-4">
                  {question.answer.map((i, e) => {
                    console.log(question.l == index[z])
                    return (
                      <button 
                      key={e}
                        onClick={() => !submit && handleclick(e)}
                        className={`text-xl p-3 ${
                          submit
                            ? question.l == index[z]
                              ? "bg-green-300 "
                              : "bg-red-300 "
                            : ""
                        } `}
                      >
                        {i}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
            <div className="flex flex-row space-x-5">

            <button
              className="text-xl bg-yellow-300 p-5"
              onClick={!submit ? handleSubmit : undefined}
            >
              {" "}
              Submit{" "}
            </button>
            {submit && (
              <button
                className="text-xl bg-yellow-300 p-5"
                onClick={handleReset}
              >
                {" "}
                Reset{" "}
              </button>
            )}
            </div>
          </>
        ) : (
          <>
          <button onClick={handleStartTest} className="text-xl bg-green-300 p-5">Start Test</button>
          <button  className="text-xl mx-4 bg-green-300 p-5">
          <SignOutButton/>
            
          </button>
          </>
        )}
      </>
    </div>
  );
};

export default IndexPage;
