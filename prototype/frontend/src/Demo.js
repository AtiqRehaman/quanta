import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import {
  Container,
  Typography,
  Button,
  Checkbox,
  FormControlLabel,
  CircularProgress,
  Card,
  CardMedia,
  CardContent,
  Grid,
  Paper,
  Box,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Alert,
  Slider,
} from "@mui/material";

function Demo() {
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [imageInfo, setImageInfo] = useState(null);
  const [useNoise, setUseNoise] = useState(false);
  const [noisePercentage, setNoisePercentage] = useState(50); // New state for noise percentage
  const [loading, setLoading] = useState(false);
  const [resultImages, setResultImages] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);
  const [time, setTime] = useState(null);
  const [timer, setTimer] = useState(0);
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);
  const intervalRef = useRef(null);

  const compressImage = (file, maxSize = 512, quality = 0.7) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement("canvas");
        let width = img.width;
        let height = img.height;

        // Resize to max 512x512 while maintaining aspect ratio
        if (width > maxSize || height > maxSize) {
          const ratio = Math.min(maxSize / width, maxSize / height);
          width = Math.round(width * ratio);
          height = Math.round(height * ratio);
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, width, height);

        // Convert to PNG with compression
        canvas.toBlob(
          (blob) => {
            const compressedFile = new File([blob], file.name, { type: "image/png" });
            console.log(`Compressed image size: ${(blob.size / 1024).toFixed(2)} KB`);
            resolve({ file: compressedFile, preview: canvas.toDataURL("image/png", quality) });
          },
          "image/png",
          quality
        );
      };
      img.onerror = () => reject(new Error("Failed to load image"));
      img.src = URL.createObjectURL(file);
    });
  };

  const validateFile = (file) => {
    if (!file) return "No file selected.";
    if (file.size > 2 * 1024 * 1024) return "File size exceeds 2MB.";
    if (!["image/png", "image/jpeg", "image/jpg"].includes(file.type))
      return "Invalid file type. Allowed: PNG, JPEG, JPG.";
    return null;
  };

  const handleImageChange = async (e) => {
    const file = e.target.files[0];
    await processImage(file);
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    await processImage(file);
  };

  const processImage = async (file) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      setImage(null);
      setImagePreview(null);
      setImageInfo(null);
      return;
    }

    const img = new Image();
    img.onload = async () => {
      if (img.width > 512 || img.height > 512) {
        setError("Image resolution exceeds 512x512 pixels.");
        setImage(null);
        setImagePreview(null);
        setImageInfo(null);
      } else {
        try {
          const { file: compressedImage, preview } = await compressImage(file, 512, 0.7);
          setImage(compressedImage);
          setImagePreview(preview);
          setImageInfo({
            name: file.name,
            size: `${(compressedImage.size / 1024).toFixed(2)} KB`,
            dimensions: `${img.width}x${img.height}`,
          });
          setError(null);
        } catch (err) {
          setError("Failed to compress image.");
          setImage(null);
          setImagePreview(null);
          setImageInfo(null);
        }
      }
    };
    img.onerror = () => {
      setError("Invalid image file.");
      setImage(null);
      setImagePreview(null);
      setImageInfo(null);
    };
    img.src = URL.createObjectURL(file);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!image) {
      setError("Please select a valid image!");
      return;
    }

    const formData = new FormData();
    formData.append("image", image);
    formData.append("use_noise", useNoise ? "true" : "false");
    if (useNoise) {
      formData.append("noise_percentage", noisePercentage / 100); // Send as decimal (0 to 1)
    }

    setLoading(true);
    setError(null);
    setResultImages([]);
    setMetrics(null);
    setTime(null);
    setProgress(0);
    setTimer(0);

    const startTime = Date.now();
    intervalRef.current = setInterval(() => {
      setTimer(Math.floor((Date.now() - startTime) / 1000));
    }, 1000);

    try {
      console.log("Starting upload...");
      const uploadStart = Date.now();
      const res = await axios.post("http://127.0.0.1:5000/process_image", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 500000, // 5 minutes
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
          console.log(`Upload progress: ${percentCompleted}%`);
        },
        onDownloadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`Download progress: ${percentCompleted}%`);
        },
      });
      const networkEnd = Date.now();
      console.log(`Network time (upload + download): ${((networkEnd - uploadStart) / 1000).toFixed(2)}s`);

      if (res.data.error) {
        throw new Error(res.data.error);
      }

      console.log(`Response size: ${(JSON.stringify(res.data).length / 1024).toFixed(2)} KB`);

      console.log("Processing response...");
      const processStart = Date.now();
      const images = res.data.images.map((img) => ({
        filename: img.name,
        data: `data:image/png;base64,${img.data}`,
      }));

      // Batch state updates
      setResultImages(images);
      setMetrics(res.data.metrics);
      setTime(res.data.time || Math.floor((Date.now() - startTime) / 1000));
      const processEnd = Date.now();
      console.log(`Frontend processing time: ${((processEnd - processStart) / 1000).toFixed(2)}s`);
    } catch (err) {
      console.error("Network Error Details:", err);
      setError(`Error: ${err.message}`);
    } finally {
      clearInterval(intervalRef.current);
      setLoading(false);
      setProgress(0);
    }
  };

  useEffect(() => {
    return () => clearInterval(intervalRef.current);
  }, []);

  return (
    <Container maxWidth="md" sx={{ textAlign: "center", py: 5 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: "bold", color: "#1976d2" }}>
        Hybrid Image Processor
      </Typography>

      <Paper
        elevation={3}
        sx={{
          p: 3,
          borderRadius: 2,
          mb: 3,
          backgroundColor: "#f5f5f5",
          border: dragActive ? "2px dashed #1976d2" : "1px solid #ccc",
        }}
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      >
        <form onSubmit={handleSubmit}>
          <Box sx={{ mb: 2 }}>
            <input
              type="file"
              accept="image/png,image/jpeg,image/jpg"
              onChange={handleImageChange}
              style={{ display: "block", margin: "0 auto" }}
              ref={fileInputRef}
              disabled={loading}
            />
            <Typography variant="caption" sx={{ color: "text.secondary" }}>
              Max resolution: 512x512 pixels | Max size: 2MB | Drag & drop supported
            </Typography>
          </Box>
          {imagePreview && (
            <Box sx={{ mt: 2, textAlign: "center" }}>
              <Typography variant="subtitle2" gutterBottom>
                Uploaded Image Preview
              </Typography>
              <Card sx={{ maxWidth: 300, margin: "auto", borderRadius: 2 }}>
                <CardMedia
                  component="img"
                  image={imagePreview}
                  alt="Uploaded image"
                  sx={{ height: "auto", maxHeight: 200, objectFit: "contain" }}
                />
                {imageInfo && (
                  <CardContent>
                    <Typography variant="body2">
                      Name: {imageInfo.name}
                    </Typography>
                    <Typography variant="body2">
                      Size: {imageInfo.size}
                    </Typography>
                    <Typography variant="body2">
                      Dimensions: {imageInfo.dimensions}
                    </Typography>
                  </CardContent>
                )}
              </Card>
            </Box>
          )}
          <Box sx={{ mb: 2, mt: 2 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={useNoise}
                  onChange={() => setUseNoise(!useNoise)}
                  color="primary"
                  disabled={loading}
                />
              }
              label="Use Noise"
            />
            {useNoise && (
              <Box sx={{ mt: 2, maxWidth: 300, margin: "auto" }}>
                <Typography variant="subtitle2" gutterBottom>
                  Noise Percentage
                </Typography>
                <Slider
                  value={noisePercentage}
                  onChange={(e, value) => setNoisePercentage(value)}
                  aria-labelledby="noise-percentage-slider"
                  valueLabelDisplay="auto"
                  step={1}
                  marks
                  min={0}
                  max={100}
                  disabled={loading}
                />
              </Box>
            )}
          </Box>
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || !image}
            sx={{ mt: 1, px: 4 }}
          >
            {loading ? <CircularProgress size={24} color="inherit" /> : "Upload & Process"}
          </Button>
          {loading && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress variant="determinate" value={progress} />
              <Typography variant="caption">{progress}% - Processing... {timer}s</Typography>
            </Box>
          )}
        </form>
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mt: 2, maxWidth: 600, margin: "auto" }}>
          {error}
        </Alert>
      )}

      {time && (
        <Typography variant="subtitle1" sx={{ mt: 2, color: "#555" }}>
          ⏱ Time taken: {time}s
        </Typography>
      )}

      {resultImages.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" gutterBottom>
            Processed Images
          </Typography>
          <Grid container spacing={3} sx={{ justifyContent: "center" }}>
            {resultImages.map((img, idx) => (
              <Grid item key={idx} xs={12} sm={6} md={4}>
                <Card sx={{ maxWidth: 300, margin: "auto", borderRadius: 2, boxShadow: 3 }}>
                  <CardMedia
                    component="img"
                    image={img.data}
                    alt={img.filename}
                    sx={{ height: "auto", maxHeight: 250, objectFit: "contain" }}
                  />
                  <CardContent>
                    <Typography variant="body2" sx={{ textAlign: "center", fontWeight: "bold" }}>
                      {img.filename}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {metrics && (
        <Paper
          elevation={2}
          sx={{
            mt: 4,
            p: 3,
            borderRadius: 2,
            maxWidth: 600,
            margin: "auto",
            backgroundColor: "#f9f9f9",
          }}
        >
          <Typography variant="h6" gutterBottom sx={{ textAlign: "center" }}>
            Metrics
          </Typography>
          <List>
            {Object.entries(metrics).map(([key, value]) => (
              <ListItem key={key} divider>
                <ListItemText
                  primary={key.replace(/_/g, ' ').toUpperCase()}
                  secondary={typeof value === 'number' ? value.toFixed(2) : value}
                  primaryTypographyProps={{ fontWeight: "bold" }}
                  secondaryTypographyProps={{ color: "textPrimary" }}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Container>
  );
}

export default Demo;