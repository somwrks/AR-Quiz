"use client";

import React, { useState, useRef, useEffect } from "react";
import Webcam from "react-webcam";
import { useSignIn, useUser } from "@clerk/nextjs";
import { PrismaClient } from "@prisma/client";
import { SignIn } from "@clerk/nextjs";

const IndexPage: React.FC = () => {
  const { user, signIn } = useSignIn();

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
      }, 1000);

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
      if (imageSrc) {
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
            alert("Cheating detected! You have lost a lifeline.");
            if (remainingLifeline === 0) {
              setTestStarted(false);
              alert("Take the test again, because you were cheating.");
            }
          }
        } catch (error) {
          console.error("Error detecting cheating:", error);
        }
      }
    }
  };
  const handleclick = (e: Number) => {
    setIndex((prevIndex) => [...prevIndex, e]);
  };
  const handleSubmit = async () => {
    setSubmit(true);
    const prisma = new PrismaClient();
    await prisma.testResult.create({
      data: {
        username: user?.username || "",
        userId: user?.id || "",
        score: index.length,
        livesLeft: remainingLifeline,
      },
    });
  };

  const [login, setLogin] = useState(true);
  // const handlelogin = async () => {
  //   try {
  //    <SignIn path="/sign-in" />
  //     setLogin(true);
  //   } catch (error) {
  //     console.error("Error signing in:", error);
  //   }
  // };
  return (
    <div>
      {!login ? (
        <>
        </>
      ) : (
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
                      return (
                        <button
                          onClick={() => !submit && handleclick(e)}
                          className={`text-xl p-3 ${
                            submit
                              ? question.l == index[z]
                                ? "bg-green-300 "
                                : "bg-red-300 "
                              : ""
                          } `}
                        >
                          {e}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
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
                  onClick={() => setTestStarted(false)}
                >
                  {" "}
                  Reset{" "}
                </button>
              )}
            </>
          ) : (
            <button onClick={handleStartTest}>Start Test</button>
          )}
        </>
      )}
    </div>
  );
};

export default IndexPage;
