// import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Container, Grid, Card, CardContent, Typography, Button, Box } from "@mui/material";
import "./App.css";
import dvMp4 from './assets/dv.mp4';

function About() {
  const navigate = useNavigate();
  // const [currentTime, setCurrentTime] = useState(new Date());

  // useEffect(() => {
  //   const timer = setInterval(() => {
  //     setCurrentTime(new Date());
  //   }, 1000); // Update every second
  //   return () => clearInterval(timer); // Cleanup on unmount
  // }, []);

  const cards = [
    {
      title: "Superdense Coding",
      short: "Quantum technique allowing two classical bits to be sent using one qubit.",
      long: "Superdense Coding is a fundamental quantum communication protocol that exploits quantum entanglement to enhance information transfer efficiency. An entangled qubit pair is pre-shared, and the sender encodes two classical bits into a single qubit using unitary operations. The receiver decodes the message with a joint measurement."
    },
    {
      title: "Video Demonstration",
      short: "Watch a demo of hybrid quantum-classical transmission."
    },
    {
      title: "Proposed Solution",
      short: "Hybrid model for efficient image transmission.",
      long: `The image is divided into small blocks for processing.
Entropy measures information content per block.
High-entropy blocks use Superdense Coding via quantum channels.
Low-entropy blocks use classical channels.
This combines quantum and classical strengths.
It optimizes bandwidth and enhances reliability.`
    }
  ];

  const handleButtonClick = (title) => {
    if (title === "Superdense Coding") {
      navigate("/superdense");
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 6, backgroundColor: "#0000001e", minHeight: "100vh" }}>
      <Box sx={{ mb: 10, textAlign: "center" }}>
        <Typography variant="h2" sx={{ fontWeight: 700, color: "#d21919ff" }}>
          About Our Project
        </Typography>
        <Typography variant="subtitle1" sx={{ color: "#cdcdcdff", mt: 1 }}>
          Innovating Image Transmission with Quantum-Classical Hybrid Technology
        </Typography>
      </Box>

      <Grid container spacing={0} direction="column" alignItems="center">
        {cards.map((card, index) => (
          <Grid item xs={12} key={index} sx={{ mt: index > 0 ? 10 : 0, maxWidth: 600 }}>
            <Card sx={{ width: "100%", boxShadow: 3, borderRadius: 2, p: 3 }}>
              <CardContent sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
                <Typography variant="h5" sx={{ fontWeight: 600, mb: 2, color: "#d6d6d6ff" }}>
                  {card.title}
                </Typography>
                <Typography variant="body2" sx={{ mb: 2, color: "#e4e4e4ff" }}>
                  {card.short}
                </Typography>

                {card.title === "Video Demonstration" && (
                  <Box sx={{ flexGrow: 1, display: "flex", justifyContent: "center", alignItems: "center", position: "relative", mb: 2 }}>
                    <video
                      controls
                      width="100%"
                      style={{
                        maxWidth: "100%",
                        height: "auto",
                        objectFit: "contain"
                      }}
                    >
                      <source
                        src={dvMp4}
                        type="video/mp4"
                      />
                      Your browser does not support the video tag.
                    </video>
                  </Box>
                )}

                {card.long && (
                  <Typography
                    variant="body2"
                    sx={{
                      mt: 2,
                      color: "#444",
                      flexGrow: 1,
                      textAlign: card.title === "Proposed Solution" ? "left" : "inherit", 
                    }}
                  >
                    {card.title === "Proposed Solution" ? (
                      <ul style={{ paddingLeft: 20 }}>
                        {card.long.split("\n").map((point, i) => (
                          <li key={i} style={{ marginBottom: 8 }}>{point.trim()}</li>
                        ))}
                      </ul>
                    ) : (
                      card.long
                    )}
                  </Typography>
                )}

                {card.title === "Superdense Coding" && (
                  <Button
                    variant="contained"
                    sx={{ mt: 2, backgroundColor: "#1976d2", "&:hover": { backgroundColor: "#1565c0" } }}
                    onClick={() => handleButtonClick(card.title)}
                  >
                    Learn More
                  </Button>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 10, textAlign: "center" }}>
        <Button
          variant="contained"
          sx={{ backgroundColor: "#1976d2", "&:hover": { backgroundColor: "#1565c0" }, px: 4, py: 1.5 }}
          onClick={() => navigate("/demo")}
        >
          Get Started
        </Button>
      </Box>

    </Container>
  );
}

export default About;